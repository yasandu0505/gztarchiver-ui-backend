def individual_product(product):
    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "category": product["category"],
        "inStock": product["inStock"]
    }
    
def all_products(products):
    return [individual_product(product) for product in products]