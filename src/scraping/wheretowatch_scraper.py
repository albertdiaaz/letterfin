import requests
from urllib.parse import urljoin

class WhereToWatchScraper:
    """
    A class to scrape movie streaming availability information from Letterboxd.
    """
    _BASE_URL = "https://letterboxd.com"
    _IMDB_PATH = "imdb"
    
    def __init__(self, imdb_id: str, country: str):
        """
        Initialize the scraper with an IMDB ID and country code.
        
        Args:
            imdb_id (str): The IMDB ID of the movie to scrape
            country (str): Country code in ISO 3166-1 alpha-3 format
        """
        self._imdb_id = imdb_id
        self._country = country
        self._movie_path: str | None = None
        self._letterboxd_id: int | None = None
        
    @property
    def imdb_id(self) -> str:
        """Get the IMDB ID."""
        return self._imdb_id
    
    @imdb_id.setter
    def imdb_id(self, value: str) -> None:
        """Set the IMDB ID."""
        self._imdb_id = value
        self._movie_path = None
        self._letterboxd_id = None
        
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
            
        return location.rstrip('/')
        
    def _get_letterboxd_id(self) -> int:
        """
        Get Letterboxd's internal ID for the movie.
        
        Returns:
            int: The Letterboxd ID
            
        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If ID cannot be extracted
        """
        if not self._movie_path:
            self._movie_path = self._get_movie_path()
            
        json_url = f"{self._movie_path}/json/"
        response = requests.get(urljoin(self._BASE_URL, json_url))
        response.raise_for_status()
        
        try:
            data = response.json()
            return int(data.get('id'))
        except (ValueError, KeyError) as e:
            raise ValueError(f"Could not extract Letterboxd ID: {str(e)}")
            
    def get_services_json(self) -> str:
        """
        Get the JSON content of streaming services availability.
        
        Returns:
            str: The JSON content with streaming services data
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        if not self._letterboxd_id:
            self._letterboxd_id = self._get_letterboxd_id()
            
        url = f"{self._BASE_URL}/s/film-availability"
        params = {
            'filmId': self._letterboxd_id,
            'locale': self._country
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text