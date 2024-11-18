# logger_config.py

import logging

def get_logger(name):
    """
    Creates and configures a logger with a specific name.
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        # Set the minimum level of logging
        logger.setLevel(logging.DEBUG)

        # Create a console handler to output logs to the terminal
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Define the log format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(console_handler)

    return logger
