from pydantic import BaseModel

class Products(BaseModel):
    name : str
    price : float
    category : str
    inStock : bool = False