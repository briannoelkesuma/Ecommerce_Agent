from contextlib import contextmanager
import logging
import os
from pathlib import Path
from typing import Generator, Optional

import sqlite3
import pandas as pd

from database.config import DEFAULT_CONFIG, DatabaseConfig

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database operations, including set up, connection and data insertion."""

    def __init__(self, config: DatabaseConfig = DEFAULT_CONFIG):
        self.config = config

    def _ensure_db_directory(self) -> None:
        """Ensures that the database directory exists."""
        db_directory = os.path.dirname(self.config.db_path)
        Path(db_directory).mkdir(parents=True, exist_ok=True)

    def create_database(self) -> bool:
        """
        Creates a new database and sets up the schema.

        Returns:
            bool: True if the database was created successfully, False otherwise.
        """
        try:
            # create db
            with self.get_connection() as conn:
                logger.info(f"Created database at: {self.config.db_path}")
            
            # create and execute schema if provided
            if self.config.schema_path:
                return self.execute_sql_file(self.config.schema_path)
            return True

        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            return False

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for database connections.

        Yields:
            sqlite3.Connection: Database connection object.
        """
        conn = None
        try:
            conn = sqlite3.connect(self.config.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            if conn:
                conn.close()

    def execute_sql_file(self, file_path: str) -> bool:
        """
        Executes an SQL script from a file.

        Args:
            file_path (str): Path to the SQL file.

        Returns:
            bool: True if the execution was successful, False otherwise.
        """
        try:
            with open(file_path, "r") as file:
                sql_script = file.read()
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return False

        try:
            with self.get_connection()  as conn:
                conn.executescript(sql_script)
                logger.info(f"Executed SQL script from: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error executing SQL script: {str(e)}")
            return False
                
    def insert_product(self, product_name: str, description: str, category: str, price: float, quantity: int) -> bool:
        """
        Inserts a single product into the database.

        Args:
            product_name (str): Name of the product
            category (str): Product category
            description (str): Product description
            price (float): Product price
            quantity (int): Available quantity

        Returns:
            bool: True if insertion was successful, False otherwise.
        """

        query = """
            INSERT INTO products (ProductName, Category, Description, Price, Quantity)
            VALUES (?, ?, ?, ?, ?);
        """
        try:
            with self.get_connection() as conn:
                conn.execute(query, (product_name.lower(), category.lower(), description, price, quantity))
                logger.info(f"Inserted product: {product_name}")
                conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error inserting product {product_name}: {e}")
            return False

    def insert_products_from_json(self, file_path: Optional[str] = None) -> bool:
        """
        Inserts products from a JSON file into the database.

        Args:
            file_path (str): Path to the JSON file containing product data.

        Returns:
            bool: True if all products were inserted successfully, False otherwise.
        """

        file_path = file_path or self.config.products_path
        if not file_path:
            logger.error("No products file path provided")
            return False

        try:
            df = pd.read_json(file_path)
        except Exception as e:
            logger.error(f"Failed to load JSON file: {str(e)}")
            return False
        
        success = True
        for _, row in df.iterrows():
            product_success = self.insert_product(
                product_name=row["product_name"],
                description=row["description"],
                category=row["category"],
                price=row["price"],
                quantity=row["quantity"],
            )
            success = product_success and success
        
        if success:
            logger.info("Inserted all products")
        else:
            logger.error("Failed to insert one or more products")
        
        return success
    