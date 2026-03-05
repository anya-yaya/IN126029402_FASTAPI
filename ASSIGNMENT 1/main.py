from fastapi import FastAPI, Query

app = FastAPI()

products =[ 
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category':'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category':'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB-Hub', 'price': 799, 'category':'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category':'Stationery', 'in_stock': True},
# 1. Add 3 more products
    {'id': 5, 'name': 'Laptop Stand', 'price': 1299, 'category':'Electronics', 'in_stock': True},
    {'id': 6, 'name': 'Mechanical Keyboard', 'price': 2499, 'category':'Electronics', 'in_stock': True},
    {'id': 7, 'name': 'Webcam', 'price': 1899, 'category':'Electronics', 'in_stock': False},
    ]

@app.get("/")
def home():
    return {"message": "Welcome to our app"}

@app.get("/products")
def get_all_products():
    return {'products': products, 'total': len(products)}

@app.get("/products/filter")
def filter_products(
    category: str = Query(None, description="Electronics or Stationery"),
    max_price: int = Query(None, description="Maximum price"),
    in_stock: bool = Query(None, description="True = in stock only")
):
    result = products

    if category:
        result = [p for p in result if p['category'] == category]
    if max_price:
        result = [p for p in result if p['price'] <= max_price]
    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
    return {'products': result, 'count': len(result)}

#3. Show only In-Stock Products
@app.get("/products/instock")
def get_in_stock_products():
    available = [p for p in products if p['in_stock'] == True]
    return {'in_stock_products': available, 'count': len(available)}

#⭐ Cheapest & Most Expensive Product
@app.get("/products/deals")
def get_deals():
    if not products:
        return {"message": "No products available"}
    cheapest = min(products, key=lambda p: p['price'])
    expensive = max(products, key=lambda p: p['price'])
    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }

#5. Search products by name
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    result = [p for p in products if keyword.lower() in p['name'].lower()]
    if not result:
        return {"Message": "No products matched your search"}
    return {'keyword': keyword, 'results': result, 'Total_matches': len(result)}

#2. Add a category filter endpoint
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):
    result = [p for p in products if p['category'] == category_name]
    if not result:
        return {"error": "No products found in this category"}
    return {'category': category_name, 'products': result, 'total': len(result)}

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {"error": "Product not found"}

#4. Build a store Info Endpoint
@app.get("/store/summary")
def get_store_summary():
    total_products = len(products)
    in_stock_count = len([p for p in products if p['in_stock']])
    out_stock_count = total_products - in_stock_count
    categories = list(set([p['category'] for p in products]))
    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock_products": in_stock_count,
        "out_of_stock_products": out_stock_count,
        "categories": categories
    }
  
