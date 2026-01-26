from typing import Dict, Any, List, Optional
from clients.query_api_client import QueryAPIClient
import logging


class DocumentService:
    """Service for document validation and relationship operations"""
    
    def __init__(self, api_client: QueryAPIClient):
        """
        Initialize document service.
        
        Args:
            api_client: Query API client instance
        """
        self.api_client = api_client
    
    def is_document_available(self, document_id: str) -> Optional[str]:
        """
        Validate document on graph and return entity ID if found. Basically check the user requested document node is exists or not.
        If exists return with the actual entity_id

        user request -> 2153-12
        expected output if the document existsts -> 2153-12_doc_34
        
        Args:
            document_id: Document ID to validate
            
        Returns:
            Entity ID if found and validated, False if not found, None on error
        """
        entity_id = self.api_client.search_entity(document_id)
        
        if entity_id:
            logging.info(f"Document Found : {entity_id}")
        else:
            logging.info(f"Document not Found : {entity_id}")
        
        return entity_id
    
    def get_document_relationships(self, document_id: str) -> Dict[str, Any]:
        """
        Get relationships for a document.
        
        Args:
            document_id: Document entity ID
            
        Returns:
            List of relationships with document numbers, or error information
        """
        relationship_response = self.api_client.get_entity_relations(document_id)
        
        if "error" in relationship_response:
            logging.error(f"Error getting relationships: {relationship_response['error']}")
            return relationship_response["error"]
        
        # Filter and enrich relationships
        filtered_relationship_response = [
            {
                "relatedEntityId": relationship["relatedEntityId"],
                "name": relationship["name"],
                "direction": relationship["direction"]
            }
            for relationship in relationship_response
        ]
        
        # Fetch document names for each relationship
        for relationship in filtered_relationship_response:
            document_name = self.api_client.get_entity_by_id(relationship["relatedEntityId"])
            if document_name:
                relationship["document_number"] = document_name
            else:
                relationship["document_number"] = False
        
        return filtered_relationship_response

