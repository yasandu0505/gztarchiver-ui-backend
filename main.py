from fastapi import FastAPI , APIRouter
from database import collection, all_products, individual_product
from bson import ObjectId

app = FastAPI()
router = APIRouter()

@router.get("/")
async def get_all_products():
    products = collection.find() 
    return all_products(products)

@router.get("/{product_id}")
async def get_individual_product(product_id : str):
    product = collection.find_one({
        "_id" : ObjectId(product_id)
    })
    if not product:
        return {
            "error" : "Product not found"
        }
    return individual_product(product)

app.include_router(router)