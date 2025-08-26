from fastapi import FastAPI , APIRouter, Query
from database import collection_names, all_docs, individual_doc , db
from bson import ObjectId
from typing import Optional

app = FastAPI()
router = APIRouter()

@router.get("/documents")
async def get_all_doc_years():
    collections_set = []
    print(f"📊 Found {len(collection_names)} collections:")
    for collection in collection_names:
        collections_set.append(collection)
    return {
        "doc_collections" : collections_set
        }

# @router.get("/documents/{doc_year}")
# async def get_all_docs_for_year(doc_year : str):
#     if doc_year not in collection_names:
#         return {
#             "error" : "Year not found"
#         }
#     collection = db[str(doc_year)]
#     docs = collection.find()
#     return all_docs(docs)

@router.get("/documents/{doc_year}")
async def get_all_docs_for_year(
    doc_year: str,
    limit: Optional[int] = Query(default=None, ge=1, le=1000, description="Number of documents per page"),
    offset: int = Query(default=0, ge=0, description="Number of documents to skip")
):
    if doc_year not in collection_names:
        return {
            "error": "Year not found"
        }
    
    collection = db[str(doc_year)]
    
    # Get total count for pagination metadata
    total_count = collection.count_documents({})
    
    # Apply pagination only if limit is provided
    if limit is not None:
        docs = collection.find().skip(offset).limit(limit)
        
        # Calculate pagination metadata
        has_next = (offset + limit) < total_count
        has_previous = offset > 0
        total_pages = (total_count + limit - 1) // limit  # Ceiling division
        current_page = (offset // limit) + 1
        
        documents = all_docs(docs)
        
        return {
            "documents": documents,
            "pagination": {
                "total_count": total_count,
                "current_page": current_page,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_previous": has_previous,
                "limit": limit,
                "offset": offset
            }
        }
    else:
        # Return all documents without pagination (your original behavior)
        docs = collection.find()
        documents = all_docs(docs)
        
        return {
            "documents": documents,
            "total_count": total_count
        }

@router.get("/documents/{doc_year}/{doc_id}")
async def get_individual_doc(doc_year : str, doc_id : str):
    if doc_year not in collection_names:
        return {
            "error" : "Year not found"
        }
    collection = db[str(doc_year)]
    doc = collection.find_one({
        "_id" : ObjectId(doc_id)
    })
    if not doc:
        return {
            "error" : "Document not found"
        }
    return individual_doc(doc)

app.include_router(router)