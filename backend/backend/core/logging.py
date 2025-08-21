import logging

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