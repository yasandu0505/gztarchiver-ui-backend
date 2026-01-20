from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # Github settings
        self.github_api: str = os.getenv("GITHUB_API", "")
        self.github_user: str = os.getenv("GITHUB_USER","")
        self.github_repository: str = os.getenv("GITHUB_REPOSITORY", "")
        self.github_api_key: str = os.getenv("GITHUB_API_KEY", "")
        self.github_target_dir: str = os.getenv("GITHUB_TARGET_DIR", "")
        self.github_target_branch: str = os.getenv("GITHUB_TARGET_BRANCH", "")
        self.github_file_download_url: str = os.getenv("GITHUB_FILE_DOWNLOAD_URL","")
        self.cache_metadata_saving_dir: str = os.getenv("CACHE_SAVING_DIR","")
        
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

