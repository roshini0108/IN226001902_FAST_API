from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# 1 - temp data to simulate a product database
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 5, "name": "Bluetooth Speaker", "price": 1499, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Desk Organizer", "price": 299, "category": "Office Supplies", "in_stock": False},
    {"id": 7, "name": "Water Bottle", "price": 199, "category": "Lifestyle", "in_stock": True},
]

feedback = []

orders = []
order_counter = 1

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


# Home route
@app.get("/")
def home():
    return {"message": "Welcome to the Product API!"}


# Get all products
@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}


# Filter products by category
@app.get("/products/categories")
def get_categories(category: str = Query(None, description="Electronics, Stationery, Office Supplies, Lifestyle")):

    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    return {"filtered_products": result, "total": len(result)}


# Filter by stock
@app.get("/products/in-stock")
def get_in_stock_products(in_stock: bool = Query(None, description="true or false")):

    result = products

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return {"filtered_products": result, "total": len(result)}


# Filter by price range
@app.get("/products/filter")
def filter_products(
    category: str = Query(None),
    min_price: int = Query(None),
    max_price: int = Query(None),
    in_stock: bool = Query(None)
):

    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return {"filtered_products": result, "total": len(result)}


# Store summary
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


# Search products
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    result = [p for p in products if keyword.lower() in p["name"].lower()]

    if not result:
        return {"message": "No products matched your search"}

    return {
        "matched_products": result,
        "total_matches": len(result)
    }


# Best deal
@app.get("/products/deals")
def product_deals():

    cheapest = min(products, key=lambda x: x["price"])
    expensive = max(products, key=lambda x: x["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }


# Product summary dashboard
@app.get("/products/summary")
def product_summary():

    total_products = len(products)

    in_stock_count = len([p for p in products if p["in_stock"]])
    out_of_stock_count = len([p for p in products if not p["in_stock"]])

    most_expensive_product = max(products, key=lambda x: x["price"])
    cheapest_product = min(products, key=lambda x: x["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {
            "name": most_expensive_product["name"],
            "price": most_expensive_product["price"]
        },
        "cheapest": {
            "name": cheapest_product["name"],
            "price": cheapest_product["price"]
        },
        "categories": categories
    }


# Product price only
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}


# Submit feedback
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data)

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: list[OrderItem]

# create order (starts as pending)

@app.post("/orders")
def create_order(product_id: int, quantity: int):

    global order_counter

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        return {"error": "Product not found"}

    order = {
        "order_id": order_counter,
        "product": product["name"],
        "quantity": quantity,
        "status": "pending"
    }

    orders.append(order)
    order_counter += 1

    return order

# get order by id

@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            return order

    return {"error": "Order not found"}

# confirm order

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return order

    return {"error": "Order not found"}

#10 - route to place bulk order

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f'{product["name"]} is out of stock'
            })
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

# Dynamic route LAST
@app.get("/products/{product_id}")
def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    return {"error": "Product not found"}