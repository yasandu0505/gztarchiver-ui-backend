import requests
import json
from typing import List, Dict, Any, Optional
from config.settings import settings
import logging

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
        """Fetch data from the global metadata URL"""
        try:
            url = settings.global_metadata_url
            if not url:
                logger.warning("GLOBAL_METADATA_URL is not set. Using empty dataset.")
                self._data = []
                return

            response = requests.get(url)
            response.raise_for_status()
            
            # The data is expected to be a list of document objects
            self._data = response.json()
            logger.info(f"Successfully loaded {len(self._data)} documents from metadata store.")
            
        except Exception as e:
            logger.error(f"Failed to fetch global metadata: {e}")
            # If we fail to fetch, we keep the old data or empty if first run
            if not self._data:
                self._data = []

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents from the store"""
        return self._data
