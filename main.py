from fastapi import FastAPI , APIRouter
from database import collection_names, all_docs, individual_doc , db
from bson import ObjectId

app = FastAPI()
router = APIRouter()

@router.get("/documents")
async def get_all_doc_years():
    collections_set = []
    print(f"📊 Found {len(collection_names)} collections:")
    for collection in collection_names:
        collections_set.append(collection)
    return {
        "collections" : collections_set
        }

@router.get("/documents/{doc_year}")
async def get_all_docs_for_year(doc_year : str):
    if doc_year not in collection_names:
        return {
            "message" : "Year not found"
        }
    collection = db[str(doc_year)]
    docs = collection.find()
    return all_docs(docs)

@router.get("/documents/{doc_year}/{doc_id}")
async def get_individual_doc(doc_year : str, doc_id : str):
    if doc_year not in collection_names:
        return {
            "message" : "Year not found"
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