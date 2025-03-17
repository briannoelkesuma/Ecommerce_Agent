from pydantic import BaseModel, Field, field_validator

# Product Model
class Product(BaseModel):
    ProductName: str = Field(..., example="Sample Product")
    Category: str = Field(..., example="Category A")
    Description: str = Field(None, example="A sample description")
    Price: float = Field(..., gt=0, example=9.99)
    Quantity: int = Field(..., ge=0, example=10)

# Order Model
class Order(BaseModel):
    CustomerId: int = Field(..., example=123)
    OrderDate: str = Field(..., example="2025-03-17T12:00:00")
    Status: str = Field(..., example="Pending")

    @field_validator("Status")
    def validate_status(cls, v):
        allowed = ["Pending", "Shipped", "Cancelled", "Completed"]
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v

# Order Detail Model
class OrderDetail(BaseModel):
    OrderId: int = Field(..., example=1)
    ProductId: int = Field(..., example=101)
    Quantity: int = Field(..., gt=0, example=1)
    UnitPrice: float = Field(..., gt=0, example=9.99)

    @field_validator("Quantity")
    def quantity_limit(cls, v):
        if v > 99:
            raise ValueError("Unfortunately, you cannot add multiple items of the same product to your cart. If you would like to place a larger order, please contact us.")
        return v

# CREATE TABLE IF NOT EXISTS products (
#     ProductId INTEGER PRIMARY KEY AUTOINCREMENT,
#     ProductName TEXT NOT NULL,
#     Category TEXT NOT NULL,
#     Description TEXT,
#     Price DOUBLE NOT NULL CHECK(Price > 0),
#     Quantity INTEGER NOT NULL CHECK(Quantity >= 0)
# );

# CREATE TABLE IF NOT EXISTS orders (
#     OrderId INTEGER PRIMARY KEY AUTOINCREMENT,
#     CustomerId INTEGER NOT NULL,
#     OrderDate TEXT NOT NULL,
#     Status TEXT NOT NULL CHECK(Status IN ('Pending', 'Shipped', 'Cancelled', 'Completed')),
#     FOREIGN KEY (CustomerId) REFERENCES Customers (CustomerId)
# );

# CREATE TABLE IF NOT EXISTS orders_details (
#     OrderDetailId INTEGER PRIMARY KEY AUTOINCREMENT,
#     OrderId INTEGER NOT NULL,
#     ProductId INTEGER NOT NULL,
#     Quantity INTEGER NOT NULL CHECK(Quantity > 0),
#     UnitPrice REAL NOT NULL CHECK(UnitPrice > 0),
#     FOREIGN KEY (OrderId) REFERENCES Orders (OrderId),
#     FOREIGN KEY (ProductId) REFERENCES Products (ProductId)
# );