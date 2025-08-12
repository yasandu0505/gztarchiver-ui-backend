from fastapi import FastAPI , APIRouter
from database import collection, all_docs, individual_doc
from bson import ObjectId

app = FastAPI()
router = APIRouter()

@router.get("/")
async def get_all_docs():
    docs = collection.find() 
    return all_docs(docs)

@router.get("/{doc_id}")
async def get_individual_doc(doc_id : str):
    doc = collection.find_one({
        "_id" : ObjectId(doc_id)
    })
    if not doc:
        return {
            "error" : "Document not found"
        }
    return individual_doc(doc)

app.include_router(router)