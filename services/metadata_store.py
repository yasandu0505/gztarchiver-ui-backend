import requests
import json
from typing import List, Dict, Any, Optional
from config.settings import settings
import logging
from database.models import Docs

logger = logging.getLogger(__name__)

class MetadataStore:
    """Service to fetch and store global metadata"""
    
    _instance = None
    _data: List[Dict[str, Any]] = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetadataStore, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the store by fetching data"""
        self.refresh_data()
        
    def refresh_data(self) -> None:
        """Fetch data from the global metadata URL and validate against Docs model"""
        try:
            url = settings.global_metadata_url
            if not url:
                logger.warning("GLOBAL_METADATA_URL is not set. Using empty dataset.")
                self._data = []
                return

            response = requests.get(url, timeout=settings.request_timeout)
            response.raise_for_status()
            
            raw_data = response.json()
            validated_data = []
            
            for item in raw_data:
                try:
                    # Validate and clean data using Pydantic model
                    # This ensures our single source of truth (Docs model) is respected
                    doc = Docs(**item)
                    validated_data.append(doc.model_dump())
                except Exception as validation_error:
                    logger.warning(f"Skipping invalid document: {validation_error}")
            
            self._data = validated_data
            logger.info(f"Successfully loaded and validated {len(self._data)} documents.")
            
        except Exception as e:
            logger.error(f"Failed to fetch global metadata: {e}")
            if not self._data:
                self._data = []
    
    @property
    def documents(self) -> List[Dict[str, Any]]:
        """Get all validated documents from the store"""
        return self._data
    
