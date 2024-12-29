from dataclasses import dataclass
from typing import List, Optional
from bs4 import BeautifulSoup
import re
from datetime import datetime
from urllib.parse import urljoin

@dataclass
class Review:
    """Class to store review information"""
    user: str
    user_image: str
    review_date: str
    review_text: str
    rating: Optional[str] = None
    likes_count: Optional[int] = None
    contains_spoilers: bool = False

class ReviewParser:
    """Parser for Letterboxd movie reviews"""
    
    _BASE_URL = "https://letterboxd.com"
    
    def __init__(self, html_content: str):
        """
        Initialize the parser with HTML content
        
        Args:
            html_content (str): The HTML content to parse
        """
        self.soup = BeautifulSoup(html_content, 'html.parser')
    
    def _extract_user_image(self, avatar_element) -> str:
        """
        Extract full URL for user profile image
        
        Args:
            avatar_element: The avatar <a> tag element
            
        Returns:
            str: Complete URL of user profile image
        """
        if not avatar_element:
            return ""
            
        img_element = avatar_element.find('img')
        if not img_element or 'src' not in img_element.attrs:
            return ""
            
        img_url = img_element['src']
        # Si la URL es relativa, la convertimos en absoluta
        if img_url.startswith('/'):
            return urljoin(self._BASE_URL, img_url)
        return img_url
    
    def _extract_rating(self, attribution_block) -> Optional[str]:
        """
        Extract rating from the attribution block
        Convert Letterboxd star rating (★) to numeric rating
        
        Returns:
            Optional[str]: Rating as a string (e.g., "4.5", "3.0") or None if no rating
        """
        rating_span = attribution_block.find('span', class_='rating')
        if not rating_span:
            return None
            
        rated_class = [c for c in rating_span['class'] if c.startswith('rated-')]
        if rated_class:
            # rated-10 -> 5.0, rated-9 -> 4.5, etc
            numeric_rating = int(rated_class[0].split('-')[1]) / 2
            return str(numeric_rating)
        
        stars_text = rating_span.get_text().strip()
        
        # Si no hay texto de estrellas
        if not stars_text:
            return None
            
        full_stars = stars_text.count('★')
        half_star = '½' in stars_text
        
        # Calcular rating
        rating = full_stars + (0.5 if half_star else 0.0)
        
        return str(rating)
    
    def _extract_likes_count(self, review_block) -> Optional[int]:
        """Extract number of likes from the review"""
        likes_element = review_block.find('p', class_='like-link-target')
        if likes_element and 'data-count' in likes_element.attrs:
            return int(likes_element['data-count'])
        return None
    
    def _clean_review_text(self, text: str) -> str:
        """Clean and format review text"""
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.replace('<br>', '\n')
        return text
    
    def _extract_review_date(self, attribution_block) -> str:
        """Extract review date from various possible formats"""
        date_span = attribution_block.find('span', class_='_nobr')
        if date_span:
            time_element = date_span.find('time')
            if time_element and 'datetime' in time_element.attrs:
                try:
                    dt = datetime.fromisoformat(time_element['datetime'].replace('Z', '+00:00'))
                    return dt.strftime('%d %b %Y')
                except ValueError:
                    pass
            
            return date_span.get_text().strip()
        return ""

    def _extract_spoiler_text(self, body_text) -> tuple[str, bool]:
        """Extract review text and check for spoilers"""
        contains_spoilers = False
        review_text = ""
        
        if not body_text:
            return review_text, contains_spoilers
            
        # Check for spoiler warning
        spoiler_p = body_text.find('p', class_='contains-spoilers')
        if spoiler_p:
            contains_spoilers = True
            hidden_div = body_text.find('div', class_='hidden-spoilers')
            if hidden_div:
                review_paragraphs = hidden_div.find_all('p')
                review_text = " ".join(p.get_text() for p in review_paragraphs)
        else:
            review_paragraphs = body_text.find_all('p')
            review_text = " ".join(p.get_text() for p in review_paragraphs)
        
        return self._clean_review_text(review_text), contains_spoilers
    
    def extract_reviews(self) -> List[Review]:
        """
        Extract all reviews from the HTML content
        
        Returns:
            List[Review]: List of Review objects containing parsed data
        """
        reviews = []
        review_elements = self.soup.find_all('li', class_='film-detail')
        
        for element in review_elements:
            avatar = element.find('a', class_='avatar')
            user = avatar['href'].strip('/') if avatar else ""
            user_image = self._extract_user_image(avatar)
            
            content_div = element.find('div', class_='film-detail-content')
            if not content_div:
                continue
                
            attribution_block = content_div.find('div', class_='attribution-block')
            body_text = content_div.find('div', class_='body-text')
            
            review_text, contains_spoilers = self._extract_spoiler_text(body_text)
            
            review = Review(
                user=user,
                user_image=user_image,
                review_date=self._extract_review_date(attribution_block),
                review_text=review_text,
                rating=self._extract_rating(attribution_block),
                likes_count=self._extract_likes_count(content_div),
                contains_spoilers=contains_spoilers
            )
            reviews.append(review)
        
        return reviews