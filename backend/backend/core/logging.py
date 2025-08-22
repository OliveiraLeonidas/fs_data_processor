import logging
from typing import Any

def setup_logging(name_log: str, level_log=logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name_log)
    logger.setLevel(level_log)
    
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level=level_log)
         
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_request(endpoint: str, **kwargs: Any) -> None:
    logger = get_logger("app.api")
    extra_info = " - ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(f"Request to {endpoint} - {extra_info}")


def log_error(error: Exception, context: str = "") -> None:
    logger = get_logger("app.error")
    context_str = f" - Context: {context}" if context else ""
    logger.error(f"Error: {str(error)}{context_str}", exc_info=True)