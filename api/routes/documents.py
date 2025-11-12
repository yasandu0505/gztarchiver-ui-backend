from fastapi import APIRouter, Depends
from services.document_service import DocumentService
from api.dependencies import get_document_service

router = APIRouter(tags=["documents"])


@router.post("/document/{documentId}")
async def search_document(
    documentId: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Search for a document by ID.
    
    Args:
        documentId: Document ID to search for
        document_service: Document service instance (injected)
        
    Returns:
        Entity ID if found, False if not found
    """
    document_output = document_service.validate_document(documentId)
    return document_output


@router.post("/document-rel/{documentId}")
async def search_document_rel(
    documentId: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Get relationships for a document.
    
    Args:
        documentId: Document entity ID
        document_service: Document service instance (injected)
        
    Returns:
        List of relationships with document numbers, or error information
    """
    relationship_response = document_service.get_document_relationships(documentId)
    return relationship_response

