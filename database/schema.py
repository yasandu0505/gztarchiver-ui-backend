def individual_doc(doc):
    return {
        "id": str(doc["_id"]),
        "document_id": doc["document_id"],
        "document_date": doc["document_date"],
        "document_type": doc["document_type"],
        "reasoning": doc["reasoning"],
        "gdrive_file_id": doc["gdrive_file_id"],
        "gdrive_file_url": doc["gdrive_file_url"],
        "download_url": doc["download_url"]
    }
    
def all_docs(docs):
    return [individual_doc(doc) for doc in docs]