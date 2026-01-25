import requests
from typing import Dict, Any, Optional, List
from config.settings import settings
from utils.protobuf_decoder import decode_protobuf


class QueryAPIClient:
    """Client for interacting with the Query API"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize Query API client.
        
        Args:
            base_url: Base URL for the Query API. If not provided, uses settings.
        """
        self.base_url = base_url or settings.query_api
        self.headers = {
            "Content-Type": "application/json",
        }
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request to the Query API.
        
        Args:
            method: HTTP method (e.g., "POST")
            endpoint: API endpoint path
            payload: Request payload
            
        Returns:
            Response JSON as dictionary, or None on error
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error making request to {url}: {str(e)}")
            return None
    
    def search_entity(self, document_id: str, kind_major: str = "Document", kind_minor: str = "") -> Optional[str]:
        """
        Search for an entity by document ID.
        
        Args:
            document_id: Document ID to search for
            kind_major: Entity kind major (default: "Document")
            kind_minor: Entity kind minor (default: "")
            
        Returns:
            Entity ID if found and validated, False if not found, None on error
        """
        payload = {
            "kind": {
                "major": kind_major,
                "minor": kind_minor
            },
            "name": document_id,
        }
        
        response = self._make_request("/v1/entities/search", payload)
        
        if not response:
            return None
        
        if response.get("body") and isinstance(response["body"], list) and len(response["body"]) > 0:
            document = response["body"][0]
            # Getting the document number from the graph (ex: 2153-12)
            encoded_document_number = document.get("name")
            if encoded_document_number:
                decoded_document_number = decode_protobuf(encoded_document_number)
                # Check whether the document number is == document id (ex: 2153-12 == 2153-12)
                if decoded_document_number == document_id:
                    # Later the return the actual doucment id (ex: 2153-12_doc_34)
                    return document["id"]
        
        return None
    
    def get_entity_by_id(self, entity_id: str) -> Optional[str]:
        """
        Get entity by ID and return decoded document name.
        
        Args:
            entity_id: Entity ID to fetch
            
        Returns:
            Decoded document name if found, False if not found, None on error
        """
        payload = {
            "id": entity_id
        }
        
        response = self._make_request("/v1/entities/search", payload)
        
        if not response:
            return None
        
        if response.get("body") and isinstance(response["body"], list) and len(response["body"]) > 0:
            document = response["body"][0]
            encoded_document_number = document.get("name")
            if encoded_document_number:
                decoded_document_number = decode_protobuf(encoded_document_number)
                if decoded_document_number:
                    return decoded_document_number
        
        return None
        
    def get_entity_relations(self, entity_id: str) -> Dict[str, Any]:
        """
        Get relationships for an entity.
        
        Args:
            entity_id: Entity ID to get relationships for
            
        Returns:
            Dictionary with relationships or error information
        """
        
        payload = {}

        response = self._make_request(f"/v1/entities/{entity_id}/relations", payload)

        if not response:
            return None

        return response
