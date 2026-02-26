from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

COOKIES_DIR = BASE_DIR / "cookies"
COOKIES_FILE = COOKIES_DIR / "cookies.json"

DATA_DIR = BASE_DIR / "data"
PRODUCTS_ID_FILE = DATA_DIR / "products_ids.json"
PRODUCTS_FILE = DATA_DIR / "products.jsonl"

LOGS_DIR = BASE_DIR / "logs"
LOGS_FILE = LOGS_DIR / "logs.log"
