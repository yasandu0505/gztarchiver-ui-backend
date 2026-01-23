from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # Global Metadata settings
        self.global_metadata_url: str = os.getenv("GLOBAL_METADATA_URL", "")
        
        # Query API settings
        self.query_api: str = os.getenv("QUERY_API", "")
        
        # Cache settings
        self.cache_ttl: int = 300  # 5 minutes in seconds
    
    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins from environment variables ending with _CORS"""
        return [
            value for key, value in os.environ.items() 
            if key.endswith("_CORS")
        ]


# Global settings instance
settings = Settings()

