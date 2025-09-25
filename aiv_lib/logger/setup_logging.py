import logging
import logging.config
import yaml
import os
from typing import Optional

# Try to import Google Cloud Logging, but make it optional
try:
    from google.cloud import logging as gcp_logging
    GCP_LOGGING_AVAILABLE = True
except ImportError:
    GCP_LOGGING_AVAILABLE = False
    print("Warning: Google Cloud Logging not available. Using local logging only.")


def setup_logging(
    name: Optional[str] = None, 
    default_level: int = logging.INFO, 
    env_key: str = 'LOG_CFG',
    config_path: str = 'logging_config.yaml'
) -> logging.Logger:
    """
    Setup logging configuration with service name differentiation and Google Cloud integration.
    
    Args:
        name: Logger name (typically __name__ from calling module)
        default_level: Default logging level if config file not found
        env_key: Environment variable key for config file path override
        config_path: Default path to YAML configuration file
        
    Returns:
        Configured logger instance
        
    Raises:
        Exception: If critical logging setup fails
    """
    service_name = os.getenv('SERVICE_NAME', 'publisher_service')
    logger_name = name or 'root'
    
    # Get logger instance (avoid duplicate handlers by checking if already configured)
    logger = logging.getLogger(logger_name)
    
    # If logger already has handlers, assume it's already configured
    if logger.handlers:
        return logger
    
    # Check for custom config file path from environment
    config_file_path = os.getenv(env_key, config_path)
    
    try:
        # Try to load YAML configuration
        if os.path.exists(config_file_path):
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logging.config.dictConfig(config)
            logger.info(f"Loaded logging configuration from {config_file_path}")
        else:
            # Fallback to basic configuration
            log_format = f'%(asctime)s - {service_name} - {logger_name} - %(levelname)s - %(message)s'
            logging.basicConfig(
                level=default_level,
                format=log_format,
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            logger.info(f"Using basic logging configuration (config file not found: {config_file_path})")
    
    except Exception as e:
        # Fallback to basic logging if YAML config fails
        log_format = f'%(asctime)s - {service_name} - {logger_name} - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=default_level,
            format=log_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logger.warning(f"Failed to load YAML config ({e}), using basic configuration")

    # Setup Google Cloud Logging if available and not in local development
    if GCP_LOGGING_AVAILABLE and not os.getenv('LOCAL_DEVELOPMENT', False):
        try:
            gcp_client = gcp_logging.Client()
            gcp_handler = gcp_logging.handlers.CloudLoggingHandler(
                gcp_client, 
                name=f"{service_name}-{logger_name}"
            )
            
            # Create formatter for GCP logs
            gcp_formatter = logging.Formatter(
                f'%(levelname)s - {service_name} - {logger_name} - %(message)s'
            )
            gcp_handler.setFormatter(gcp_formatter)
            
            # Add handler to root logger to capture all logs
            root_logger = logging.getLogger()
            root_logger.addHandler(gcp_handler)
            
            logger.info("Google Cloud Logging initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Google Cloud Logging: {e}")
    
    elif os.getenv('LOCAL_DEVELOPMENT', False):
        logger.info("Local development mode - skipping Google Cloud Logging")
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance. If logging not already setup, initialize it.
    
    Args:
        name: Logger name (typically __name__ from calling module)
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name or 'root')
    
    # If no handlers exist, setup logging first
    if not logger.handlers and not logging.getLogger().handlers:
        return setup_logging(name)
    
    return logger


if __name__ == "__main__":
    # Test the logging setup
    test_logger = setup_logging(__name__)
    test_logger.info("Logging setup test - INFO level")
    test_logger.warning("Logging setup test - WARNING level")
    test_logger.error("Logging setup test - ERROR level")
    
    # Test getting logger without setup
    another_logger = get_logger("test_module")
    another_logger.info("Test from get_logger function")
