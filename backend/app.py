import sys
import os

# Add the parent directory (which contains the backend folder) to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    
from fastapi import FastAPI
from routes import products, orders

app = FastAPI(
    title="Store API",
    description="API for managing products and orders",
    version="1.0"
)

# Include routers on distinct paths
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)