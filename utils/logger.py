import sys
from loguru import logger

logger.remove()

def get_logger(debug=False):
    logger.add(sys.stderr, level=("DEBUG" if debug else "INFO"))
    
    return logger