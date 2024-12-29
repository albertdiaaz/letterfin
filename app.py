from src.scraping import MovieScraper, WhereToWatchScraper
from src.parser import ReviewParser, WhereToWatchParser
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def print_review(review):
    try:
        print(f"User: {review.user}")
        print(f"Profile Image: {review.user_image}")
        print(f"Rating: {review.rating}")
        print(f"Date: {review.review_date}")
        if review.contains_spoilers:
            print("Contains Spoilers: Yes")
        print(f"Review: {review.review_text}")
        print(f"Likes: {review.likes_count}")
        print("-" * 50)
    except UnicodeEncodeError as e:
        print(f"User: {review.user}")
        print(f"Profile Image: {review.user_image}")
        print(f"Rating: {review.rating}")
        print(f"Date: {review.review_date}")
        if review.contains_spoilers:
            print("Contains Spoilers: Yes")
        print(f"Review: {review.review_text.encode('ascii', 'replace').decode('ascii')}")
        print(f"Likes: {review.likes_count}")
        print("-" * 50)

def print_streaming_services(services):
    print("\nSTREAMING SERVICES AVAILABILITY:")
    print("=" * 50)
    
    if 'stream' in services:
        print("\nAvailable on streaming platforms:")
        for service in services['stream']:
            print(f"- {service.name} ({service.format}) Icon: {service.icon}")
    
    if 'rent' in services:
        print("\nAvailable for rent:")
        for service in services['rent']:
            print(f"- {service.name}: {service.price}{service.currency} ({service.format}) Icon: {service.icon}")
    
    if 'buy' in services:
        print("\nAvailable for purchase:")
        for service in services['buy']:
            print(f"- {service.name}: {service.price}{service.currency} ({service.format}) Icon: {service.icon}")
    
    print("=" * 50)

def main():
    imdb_id = "tt1375666"  
    country = "USA"        
    
    print("MOVIE REVIEWS:")
    print("=" * 50)
    
    review_scraper = MovieScraper(imdb_id)
    html = review_scraper.get_reviews_html()
    
    review_parser = ReviewParser(html)
    reviews = review_parser.extract_reviews()
    
    for review in reviews:
        print_review(review)
        
    wtw_scraper = WhereToWatchScraper(imdb_id, country)
    json_content = wtw_scraper.get_services_json()
    
    wtw_parser = WhereToWatchParser(json_content)
    services = wtw_parser.get_services()
    
    print_streaming_services(services)

if __name__ == "__main__":
    main()