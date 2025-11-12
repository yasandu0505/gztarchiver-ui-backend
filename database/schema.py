from typing import Dict, Any, List


def serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize a MongoDB document to API response format.
    
    Args:
        doc: MongoDB document dictionary
        
    Returns:
        Serialized document dictionary
    """
    return {
        "id": str(doc.get("_id", "")),
        "document_id": doc.get("document_id"),
        "description": doc.get("description"),
        "document_date": doc.get("document_date"),
        "document_type": doc.get("document_type"),
        "file_path": doc.get("file_path"),
        "download_url": doc.get("download_url"),
        "source": doc.get("source"),
        "availability": doc.get("availability"),
        "score": doc.get("score", 0)
    }


def individual_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize a single document (legacy function for backward compatibility).
    
    Args:
        doc: MongoDB document dictionary
        
    Returns:
        Serialized document dictionary
    """
    return {
        "id": str(doc.get("_id", "")),
        "document_id": doc.get("document_id"),
        "document_description": doc.get("description"),
        "document_date": doc.get("document_date"),
        "document_type": doc.get("document_type"),
        "reasoning": doc.get("reasoning"),
        "file_path": doc.get("file_path"),
        "download_url": doc.get("download_url"),
        "source": doc.get("source"),
        "availability": doc.get("availability")
    }


def all_docs(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Serialize a list of documents (legacy function for backward compatibility).
    
    Args:
        docs: List of MongoDB document dictionaries
        
    Returns:
        List of serialized document dictionaries
    """
    return [individual_doc(doc) for doc in docs]