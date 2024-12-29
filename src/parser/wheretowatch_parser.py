from dataclasses import dataclass
from typing import List, Optional, Dict
import json

@dataclass
class StreamingService:
    """Class to store streaming service information"""
    name: str
    icon: str
    locale: str
    viewUrl: str
    format: str
    type: str
    price: Optional[float]
    currency: str

class WhereToWatchParser:
    """Parser for Letterboxd streaming services availability"""
    
    def __init__(self, json_content: str):
        """
        Initialize the parser with JSON content
        
        Args:
            json_content (str): The JSON content to parse
        """
        self._content = json_content
        
    def _parse_service(self, service_data: dict) -> StreamingService:
        """
        Parse a single streaming service entry
        
        Args:
            service_data (dict): Dictionary with service data
            
        Returns:
            StreamingService: Parsed service information
        """
        return StreamingService(
            name=service_data.get('name', ''),
            icon=service_data.get('icon', ''),
            locale=service_data.get('locale', ''),
            viewUrl=service_data.get('viewUrl', ''),
            format=service_data.get('format', ''),
            type=service_data.get('type', ''),
            price=float(service_data['price']) if service_data.get('price') else None,
            currency=service_data.get('currency', '')
        )
    
    def get_services(self) -> Dict[str, List[StreamingService]]:
        """
        Extract all streaming services from the JSON content
        
        Returns:
            Dict[str, List[StreamingService]]: Dictionary with streaming options by type
            
        Raises:
            ValueError: If data cannot be parsed
        """
        try:
            data = json.loads(self._content)
            best_data = data.get('best', {})
            
            result = {}
            
            for category in ['stream', 'rent', 'buy']:
                if category in best_data:
                    services = [
                        self._parse_service(service_data) 
                        for service_data in best_data[category]
                    ]
                    result[category] = services
                    
            return result
            
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Could not parse streaming services data: {str(e)}")