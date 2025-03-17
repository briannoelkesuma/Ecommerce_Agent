from fastapi import APIRouter, HTTPException
from models import Order, OrderDetail
from backend.database.db_manager import DatabaseManager
from backend.database.config import DEFAULT_CONFIG

router = APIRouter()

# Instantiate the DatabaseManager
db_manager = DatabaseManager(config=DEFAULT_CONFIG)

# Orders Endpoints

@router.get("/", summary="Get all orders")
def get_all_orders():
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders")
        orders = [dict(row) for row in cursor.fetchall()]
    return orders

@router.get("/{order_id}", summary="Get a specific order with its details")
def get_order(order_id: int):
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE OrderId = ?", (order_id,))
        order = cursor.fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        order_data = dict(order)
        # Fetch order details
        cursor.execute("SELECT * FROM orders_details WHERE OrderId = ?", (order_id,))
        details = [dict(row) for row in cursor.fetchall()]
    return {"order": order_data, "details": details}

@router.post("/", summary="Create a new order")
def create_order(order: Order):
    query = """
        INSERT INTO orders (CustomerId, OrderDate, Status)
        VALUES (?, ?, ?);
    """
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, (order.CustomerId, order.OrderDate, order.Status))
            conn.commit()
            order_id = cursor.lastrowid
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating order: {e}")
    return {"message": "Order created successfully", "OrderId": order_id}

@router.put("/{order_id}", summary="Update an existing order")
def update_order(order_id: int, order: Order):
    query = """
        UPDATE orders
        SET CustomerId = ?, OrderDate = ?, Status = ?
        WHERE OrderId = ?;
    """
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE OrderId = ?", (order_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Order not found")
        try:
            cursor.execute(query, (order.CustomerId, order.OrderDate, order.Status, order_id))
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating order: {e}")
    return {"message": "Order updated successfully", "OrderId": order_id}

@router.delete("/{order_id}", summary="Delete an order")
def delete_order(order_id: int):
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE OrderId = ?", (order_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Order not found")
        try:
            cursor.execute("DELETE FROM orders WHERE OrderId = ?", (order_id,))
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting order: {e}")
    return {"message": "Order deleted successfully", "OrderId": order_id}

# Order Details Endpoints

@router.post("/details", summary="Add an order detail")
def add_order_detail(order_detail: OrderDetail):
    query = """
        INSERT INTO orders_details (OrderId, ProductId, Quantity, UnitPrice)
        VALUES (?, ?, ?, ?);
    """
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, (
                order_detail.OrderId,
                order_detail.ProductId,
                order_detail.Quantity,
                order_detail.UnitPrice,
            ))
            conn.commit()
            detail_id = cursor.lastrowid
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding order detail: {e}")
    return {"message": "Order detail added successfully", "OrderDetailId": detail_id}
