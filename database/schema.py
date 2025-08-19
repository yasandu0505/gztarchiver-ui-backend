def individual_doc(doc):
    return {
        "id": str(doc["_id"]),
        "document_id": doc["document_id"],
        "document_description" : doc["description"],
        "document_date": doc["document_date"],
        "document_type": doc["document_type"],
        "reasoning": doc["reasoning"],
        "file_path": doc["file_path"],
        "download_url": doc["download_url"],
        "source": doc["source"],
        "availability": doc["availability"]
    }
    
def all_docs(docs):
    return [individual_doc(doc) for doc in docs]