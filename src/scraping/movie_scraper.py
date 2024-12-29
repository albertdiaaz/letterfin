import requests
from urllib.parse import urljoin
from dataclasses import dataclass
from typing import Optional

@dataclass
class MovieScraper:
    """
    A class to scrape movie information and reviews from Letterboxd.
    """
    _BASE_URL = "https://letterboxd.com"
    _IMDB_PATH = "imdb"
    
    def __init__(self, imdb_id: str):
        """
        Initialize the scraper with an IMDB ID.
        
        Args:
            imdb_id (str): The IMDB ID of the movie to scrape
        """
        self._imdb_id = imdb_id
        self._movie_path: Optional[str] = None
        
    @property
    def imdb_id(self) -> str:
        """Get the IMDB ID."""
        return self._imdb_id
    
    @imdb_id.setter
    def imdb_id(self, value: str) -> None:
        """Set the IMDB ID."""
        self._imdb_id = value
        self._movie_path = None  
        
    @property
    def movie_path(self) -> Optional[str]:
        """Get the movie path."""
        return self._movie_path
    
    def _get_movie_path(self) -> str:
        """
        Get the Letterboxd movie path from IMDB ID.
        
        Returns:
            str: The movie path
        
        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If the location header is not found
        """
        imdb_url = urljoin(self._BASE_URL, f"{self._IMDB_PATH}/{self._imdb_id}/")
        response = requests.get(imdb_url, allow_redirects=False)
        
        if response.status_code != 302:
            raise ValueError(f"Expected 302 redirect, got {response.status_code}")
            
        location = response.headers.get('location')
        if not location:
            raise ValueError("Location header not found in response")
            
        return location
    
    def get_reviews_url(self) -> str:
        """
        Get the URL for the movie's reviews page.
        
        Returns:
            str: The complete URL for the movie's reviews
            
        Raises:
            ValueError: If movie path hasn't been fetched yet
        """
        if not self._movie_path:
            self._movie_path = self._get_movie_path()
            
        reviews_path = f"{self._movie_path.rstrip('/')}/reviews/by/activity/"
        return urljoin(self._BASE_URL, reviews_path)
    
    def get_reviews_html(self) -> str:
        """
        Get the HTML content of the reviews page.
        
        Returns:
            str: The HTML content of the reviews page
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        reviews_url = self.get_reviews_url()
        response = requests.get(reviews_url)
        response.raise_for_status()
        return response.text