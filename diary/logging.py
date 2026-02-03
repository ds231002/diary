import logging
from typing import Literal

def setup_logging(
    log_file: str = "app.log",
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
    overwrite: bool = False,
    console: bool = True
) -> None:
    numeric_level = getattr(logging, level)

    mode = "w" if overwrite else "a"

    handlers = [logging.FileHandler(log_file, mode=mode)]
    if console:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers
    )

"""
usage example:
import logging

logger = logging.getLogger(__name__)

logging.debug("message")
logging.info("message")
logging.warning("message")
logging.error("message")
logging.critical("message")
"""

"""
app.py

from utils.logging import setup_logging
setup_logging()

nlp.py

logger = logging.getLogger(__name__)
logger.info(f"header: '{header!r}'")
"""