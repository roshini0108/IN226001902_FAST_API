from fastapi import FastAPI, Query

app= FastAPI()

#1 - temp data to simulate a product database

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499 , "category": "Electronics","in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 5, "name": "Bluetooth Speaker", "price": 1499, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Desk Organizer", "price": 299, "category": "Office Supplies", "in_stock": False},
    {"id": 7, "name": "Water Bottle", "price": 199, "category": "Lifestyle", "in_stock": True},
]
#home route
@app.get("/")
def home():
    return {"message": "Welcome to the Product API!"}
#route to get all products
@app.get("/products")
def get_all_products():
    return {'products': products, 'total': len(products)}

#2 - route to filter products by category

@app.get("/products/categories")
def get_categories(category: str = Query(None, description="Electronics, Stationery, Office Supplies, Lifestyle")):
    
    result = products
    
    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    return {'filtered_products': result, 'total': len(result)}

#3 - route to filter products by stock availability

@app.get("/products/in-stock")
def get_in_stock_products(in_stock: bool = Query(None, description="true or false")):
    
    result = products
    
    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return {'filtered_products': result, 'total': len(result)}

#route to filter products by price range

@app.get("/products/filter")
def filter_products(
    category: str = Query(None, description="Electronics, Stationery, Office Supplies, Lifestyle"),
    max_price: int = Query(None, description="Maximum price of the product"),
    in_stock: bool = Query(None, description="Filter by stock availability (true/false)")
):
    
    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return {'filtered_products': result, 'total': len(result)}

#4 - route to get store summary

@app.get("/store/summary")
def store_summary():

    total_products = len(products)

    in_stock_count = len([p for p in products if p["in_stock"]])

    out_of_stock_count = len([p for p in products if not p["in_stock"]])

    categories = list(set(p["category"] for p in products))

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": in_stock_count,
        "out_of_stock": out_of_stock_count,
        "categories": categories
    }

#route to get product details by ID

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return {"error": "Product not found"}

#5 - route to search products by keyword

@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    result = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not result:
        return {"message": "No products matched your search"}

    return {
        "matched_products": result,
        "total_matches": len(result)
    }

#6 - route to get best deal and premium pick

@app.get("/products/deals")
def product_deals():

    cheapest = min(products, key=lambda x: x["price"])
    expensive = max(products, key=lambda x: x["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }
