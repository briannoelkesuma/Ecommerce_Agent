from dataclasses import dataclass
from typing import Optional
from pathlib import Path

# Calculate the project root (adjust as necessary)
BASE_DIR = Path(__file__).resolve().parent.parent  # assuming config.py is in backend/database/

@dataclass
class DatabaseConfig:
    db_name: str
    db_path: str
    schema_path: Optional[str] = None
    products_path: Optional[str] = None

DEFAULT_CONFIG = DatabaseConfig(
    db_name="store.db",
    db_path=str(BASE_DIR / "database" / "db" / "store.db"),
    schema_path=str(BASE_DIR / "database" / "db" / "schemas.sql"),
    products_path=str(BASE_DIR / "database" / "db" / "products.json"),
)