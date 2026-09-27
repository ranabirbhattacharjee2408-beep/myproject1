import logging
import traceback

from config import DATA_DIR


log_dir = DATA_DIR / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=log_dir / "jarvis.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

def log_info(message):
    """Log normal events."""
    logging.info(message)

def log_warning(message):
    """Log warnings."""
    logging.warning(message)

def log_error(feature, error):
    """Log exceptions with traceback."""
    logging.error(f"[{feature}] {error}")
    logging.error(traceback.format_exc())