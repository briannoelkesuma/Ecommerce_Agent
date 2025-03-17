from fastapi import APIRouter, HTTPException
from models import Product
from backend.database.db_manager import DatabaseManager
from backend.database.config import DEFAULT_CONFIG

router = APIRouter()

# Instantiate the DatabaseManager
db_manager = DatabaseManager(config=DEFAULT_CONFIG)

@router.get("/", summary="Get all products")
def get_all_products():
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        products = [dict(row) for row in rows]
    return products

@router.get("/{product_id}", summary="Get a specific product")
def get_product(product_id: int):
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE ProductId = ?", (product_id,))
        row = cursor.fetchone()
    if row:
        return dict(row)
    raise HTTPException(status_code=404, detail="Product not found")

@router.post("/", summary="Add a new product")
def add_product(product: Product):
    query = """
        INSERT INTO products (ProductName, Category, Description, Price, Quantity)
        VALUES (?, ?, ?, ?, ?);
    """
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, (
                product.ProductName,
                product.Category,
                product.Description,
                product.Price,
                product.Quantity,
            ))
            conn.commit()
            product_id = cursor.lastrowid
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding product: {e}")
    return {"message": "Product added successfully", "ProductId": product_id}

@router.put("/{product_id}", summary="Update an existing product")
def update_product(product_id: int, product: Product):
    query = """
        UPDATE products
        SET ProductName = ?, Category = ?, Description = ?, Price = ?, Quantity = ?
        WHERE ProductId = ?;
    """
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE ProductId = ?", (product_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Product not found")
        try:
            cursor.execute(query, (
                product.ProductName,
                product.Category,
                product.Description,
                product.Price,
                product.Quantity,
                product_id,
            ))
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating product: {e}")
    return {"message": "Product updated successfully", "ProductId": product_id}

@router.delete("/{product_id}", summary="Delete a product")
def delete_product(product_id: int):
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE ProductId = ?", (product_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Product not found")
        try:
            cursor.execute("DELETE FROM products WHERE ProductId = ?", (product_id,))
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting product: {e}")
    return {"message": "Product deleted successfully", "ProductId": product_id}
