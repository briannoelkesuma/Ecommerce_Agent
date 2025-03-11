import time
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List, Union
from database.db_manager import DatabaseManager
from pinecone import Pinecone
from langchain_openai.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

db_manager = DatabaseManager()

configuration = None

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "tershine"
pinecone_index = pc.Index(index_name)

embedding_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model='text-embedding-3-small')

@tool
def retrieve_faq_context_from_vectorstore(query_text: str, top_k: int = 3) -> str:
    """Retrieve FAQ Context from the Tershine washing guide vector store based on the query text."""
    # Embed the query text
    query_embedding = embedding_model.embed_query(query_text)

    pinecone_results = pinecone_index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    # Retrieve text and calculate similarity for the top result
    retrieved_texts = " ".join([result['metadata']['content'] for result in pinecone_results['matches']])
        
    return retrieved_texts

@tool
def add_product_to_cart(product_name: str):
    """
    Add a product to the cart.
    This function uses a persistent Chrome profile to ensure the cart state is saved.
    It adds the product and then retrieves any free shipping information (if available),
    but it does not proceed to checkout.
    """
    chrome_options = Options()
    profile_path = "path/to/persistent/profile"  # replace with your desired persistent profile path
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://tershine.com/")
        # Locate and use the search box
        clickable_search_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.input"))
        )
        clickable_search_box.clear()
        clickable_search_box.send_keys(product_name)
        # Wait for search results and click the first result
        search_results = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.search-result"))
        )
        first_link = WebDriverWait(search_results, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "li a"))
        )
        first_link.click()
        # Wait for product page to load and click buy button
        product_page = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.action"))
        )
        buy_button = WebDriverWait(product_page, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.button.buy"))
        )
        buy_button.click()
        # Wait for cart pop-up and try to capture free shipping info
        cart_pop_up = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.section.footer"))
        )
        try:
            free_shipping_info = WebDriverWait(cart_pop_up, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.shipping-information__remaining"))
            )
            free_shipping_texts = free_shipping_info.text
        except Exception:
            free_shipping_texts = "No free shipping information available."
        # Instead of clicking checkout here, simply return shipping details and current URL.
        cart_url = driver.current_url  # Alternatively, you could set this to a dedicated cart page URL if available.
        return free_shipping_texts, cart_url
    finally:
        # Optionally keep the driver open if you want to preserve session state.
        pass

@tool
def get_available_categories() -> Dict[str, List[str]]:
    """Returns a list of available product categories."""
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT DISTINCT Category 
            FROM products
            WHERE Quantity > 0
            """)
        categories = cursor.fetchall()
        return {"categories": [category["Category"] for category in categories]}

@tool
def search_products(query: Optional[str] = None, category: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None) -> Dict[str, Any]:
    """
    Searches for products based on various criteria.

    Arguments:
        query (Optional[str]): The query to search for which can be product name or description.
        category (Optional[str]): Filter by product category.
        min_price (Optional[float]): The minimum price filter.
        max_price (Optional[float]): The maximum price filter.

    Returns:
        Dict[str, Any]: Search results with products and metadata

    Example: 
        search_products(query="banana", category="fruits", max_price=5.00)
    """
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()

        query_parts = ["SELECT * FROM products WHERE Quantity > 0"]
        params = []

        if query:
            query_parts.append(
            """
            AND (
                LOWER(ProductName) LIKE ?
                OR 
                LOWER(Description) LIKE ?
            )
            """)
            search_term = f"%{query.lower()}%"
            params.extend([search_term, search_term])

        if category:
            query_parts.append(f"AND Category = ?")
            params.append(category)
        if min_price:
            query_parts.append(f"AND Price >= ?")
            params.append(min_price)
        if max_price:
            query_parts.append(f"AND Price <= ?")
            params.append(max_price)

        query_string = " ".join(query_parts)
        cursor.execute(query_string, params)
        products = cursor.fetchall()

        # Get available categories for metadata
        cursor.execute(
            """
            SELECT DISTINCT Category, COUNT(*) as count 
            FROM products 
            WHERE Quantity > 0 
            GROUP BY Category
            """
        )
        categories = cursor.fetchall()

        # Get price range for metadata
        cursor.execute(
            """
            SELECT 
                MIN(Price) as min_price,
                MAX(Price) as max_price,
                AVG(Price) as avg_price
            FROM products
            WHERE Quantity > 0
        """
        )
        price_stats = cursor.fetchone()

        return {
            "status": "success",
            "products": [
                {
                    "product_id": str(product["ProductId"]),
                    "name": product["ProductName"],
                    "category": product["Category"],
                    "description": product["Description"],
                    "price": product["Price"],
                    "stock": product["Quantity"]
                }
                for product in products
            ],
            "metadata": {
                "total_results": len(products),
                "categories": [
                    {"name": cat["Category"], "product_count": cat["count"]}
                    for cat in categories
                ],
                "price_range": {
                    "min": float(price_stats["min_price"]),
                    "max": float(price_stats["max_price"]),
                    "average": round(float(price_stats["avg_price"]), 2)
                }
            }
        }

@tool
def search_products_recommendations(config: RunnableConfig) -> Dict[str, str]:
    """Searches for product recommendations for the customer."""
    configuration = config.get("configurable", {})

    if not configuration:
        raise ValueError("Configuration is not set.")

    customer_id = configuration.get("customer_id", None)

    if not customer_id:
        raise ValueError("No Customer ID configured.")
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()

        # Get customer's previous purchases
        cursor.execute(
            """
            SELECT DISTINCT p.Category
            FROM orders o
            JOIN orders_details od ON o.OrderId = od.OrderId
            JOIN products p ON od.ProductId = p.ProductId
            WHERE o.CustomerId = ?
            ORDER BY o.OrderDate DESC
            LIMIT 3
            """,
            (customer_id,),
        )

        favourite_categories = cursor.fetchall()

        if not favourite_categories:
            # TODO: Work in Progress!
            # If no purchase history, recommend popular products
            cursor.execute(
                """
                SELECT
                    ProductId,
                    ProductName,
                    Category,
                    Description,
                    Price,
                    Quantity
                FROM products
                WHERE Quantity > 0
                ORDER BY RANDOM()
                LIMIT 5
                """
            )
        else:
            # Recommend products from favorite categories
            placeholders = ",".join("?" * len(favourite_categories))
            categories = [cat["Category"] for cat in favourite_categories]

            cursor.execute(
                f"""
                SELECT
                    ProductId,
                    ProductName,
                    Category,
                    Description,
                    Price,
                    Quantity
                FROM products
                WHERE Quantity > 0
                AND Category IN ({placeholders})
                ORDER BY RANDOM()
                LIMIT 5
                """,
                categories,
            )
        
        recommendations = cursor.fetchall()

        return {
            "status": "success",
            "customer_id": str(customer_id),
            "recommendations": [
                {
                    "product_id": str(product["ProductId"]),
                    "name": product["ProductName"],
                    "category": product["Category"],
                    "description": product["Description"],
                    "price": float(product["Price"]),
                    "stock": product["Quantity"]
                }
                for product in recommendations
            ]
        }

# @tool
# def create_order(products: List[Dict[str, Any]], *, config: RunnableConfig) -> Dict[str, str]:
#     """
#     Create a new order (product purchase for the customer).

#     Arguments:
#         products (List[Dict[str, Any]]): List of products to purchase.

#     Returns:
#         Dict[str, str]: Order details including status and message.

#     Example:
#         create_order([{"ProductName": "Product A", "Quantity": 2}, {"ProductName": "Product B", "Quantity": 1}])
#     """

#     configuration = config.get("configurable", {})
    
#     if not configuration:
#         raise ValueError("Configuration is not set.")

#     customer_id = configuration.get("customer_id", None)

#     if not customer_id:
#         raise ValueError("No Customer ID configured.")

#     with db_manager.get_connection() as conn:
#         cursor = conn.cursor()
#         try:
#             # Start transaction
#             conn.execute("BEGIN TRANSACTION")

#             # Create order
#             cursor.execute(
#                 """
#                 INSERT INTO orders (CustomerId, OrderDate, Status)
#                 VALUES (?, ?, ?)
#                 """,
#                 (customer_id, datetime.now().isoformat(), "Pending"),
#             )
#             order_id = cursor.lastrowid

#             total_amount = Decimal("0")
#             ordered_products = []

#             # Process each product
#             for item in products:
#                 product_name = item["ProductName"]
#                 quantity = item["Quantity"]

#                 # Get product details
#                 cursor.execute(
#                     "SELECT ProductId, Price, Quantity FROM products WHERE LOWER(ProductName) = LOWER(?)",
#                     (product_name,),
#                 )
#                 product = cursor.fetchone()

#                 if not product:
#                     raise ValueError(f"Product not found: {product_name}")

#                 if product["Quantity"] < quantity:
#                     raise ValueError(f"Insufficient stock for {product_name}")

#                 # Add order detail
#                 cursor.execute(
#                     """INSERT INTO orders_details (OrderId, ProductId, Quantity, UnitPrice) 
#                        VALUES (?, ?, ?, ?)""",
#                     (order_id, product["ProductId"], quantity, product["Price"]),
#                 )

#                 # Update inventory
#                 cursor.execute(
#                     "UPDATE products SET Quantity = Quantity - ? WHERE ProductId = ?",
#                     (quantity, product["ProductId"]),
#                 )

#                 total_amount += Decimal(str(product["Price"])) * Decimal(str(quantity))
#                 ordered_products.append(
#                     {
#                         "name": product_name,
#                         "quantity": quantity,
#                         "unit_price": float(product["Price"]),
#                     }
#                 )

#             cursor.execute("COMMIT")

#             return {
#                 "order_id": str(order_id),
#                 "status": "success",
#                 "message": "Order created successfully",
#                 "total_amount": float(total_amount),
#                 "products": ordered_products,
#                 "customer_id": str(customer_id),
#             }

#         except Exception as e:
#             cursor.execute("ROLLBACK")
#             return {
#                 "status": "error",
#                 "message": str(e),
#                 "customer_id": str(customer_id),
#             }

# ---------------------------------------------------------------------
# Revised create_order: creates the DB order then reopens the browser session
# to load the cart (using the same persistent profile) and clicks through to checkout.
@tool
def create_order(config: RunnableConfig) -> Dict[str, Any]:
    """
    Create a new order by first processing the products in the database,
    and then reopening the browser session (with the persistent cart)
    to click the checkout button.
    
    Returns order details along with the checkout URL.
    """
    configuration = config.get("configurable", {})
    if not configuration:
        raise ValueError("Configuration is not set.")
    customer_id = configuration.get("customer_id", None)
    if not customer_id:
        raise ValueError("No Customer ID configured.")
    
    # Reopen the browser with the persistent session so the cart is intact
    chrome_options = Options()
    profile_path = "path/to/persistent/profile"  # ensure this matches the profile used in add_product_to_cart
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        # Navigate to the cart page (or the main site if cart state is preserved)
        driver.get("https://tershine.com/sv/checkout")

        WebDriverWait(driver, 20).until(EC.url_contains("checkout"))

        while True:
            time.sleep(1)
    except Exception as ex:
        checkout_url = "Error retrieving checkout URL: " + str(ex)
    finally:
        driver.quit()

@tool
def check_order_status(order_id: Union[str, None], *, config: RunnableConfig) -> Dict[str, Union[str, None]]:
    """
    Checks the status of a specific order or all customer orders.

    Arguments:
        order_id (Union[str, None]): The ID of the order to check. If None, all customer orders will be returned.
    """
    configuration = config.get("configurable", {})
    
    if not configuration:
        raise ValueError("Configuration is not set.")

    customer_id = configuration.get("customer_id", None)

    if not customer_id:
        raise ValueError("No Customer ID configured.")

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()

        if order_id:
            # Query specific order
            cursor.execute(
                """
                SELECT 
                    o.OrderId,
                    o.OrderDate,
                    o.Status,
                    GROUP_CONCAT(p.ProductName || ' (x' || od.Quantity || ')') as Products,
                    SUM(od.Quantity * od.UnitPrice) as TotalAmount
                FROM orders o
                JOIN orders_details od ON o.OrderId = od.OrderId
                JOIN products p ON od.ProductId = p.ProductId
                WHERE o.OrderId = ? AND o.CustomerId = ?
                GROUP BY o.OrderId
            """,
                (order_id, customer_id),
            )

            order = cursor.fetchone()
            if not order:
                return {
                    "status": "error",
                    "message": "Order not found",
                    "customer_id": str(customer_id),
                    "order_id": str(order_id),
                }

            return {
                "status": "success",
                "order_id": str(order["OrderId"]),
                "order_date": order["OrderDate"],
                "order_status": order["Status"],
                "products": order["Products"],
                "total_amount": float(order["TotalAmount"]),
                "customer_id": str(customer_id),
            }
        
        else:
            # Query all customer orders
            cursor.execute(
                """
                SELECT
                    o.OrderId,
                    o.OrderDate,
                    o.Status,
                    COUNT(od.OrderDetailId) as ItemCount,
                    SUM(od.Quantity * od.UnitPrice) as TotalAmount
                FROM orders o
                JOIN orders_details od ON o.OrderId = od.OrderId
                WHERE o.CustomerId = ?
                GROUP BY o.OrderId
                ORDER BY o.OrderDate DESC
            """,
                (customer_id,),
            )

            orders = cursor.fetchall()
            return {
                "status": "success",
                "customer_id": str(customer_id),
                "orders": [
                    {
                        "order_id": str(order["OrderId"]),
                        "order_date": order["OrderDate"],
                        "status": order["Status"],
                        "item_count": order["ItemCount"],
                        "total_amount": float(order["TotalAmount"]),
                    }
                    for order in orders
                ],
            }