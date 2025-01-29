import logging
import logging.config
import yaml
import os
from google.cloud import logging as gcp_logging

service_name = os.getenv('SERVICE_NAME', 'publisher_service')

def setup_logging():
    default_level=print, env_key='LOG_CFG'
    default_path='logging_config.yaml'
    """Setup logging configuration with service name differentiation"""
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level, format=f'%(asctime)s - {service_name} - %(levelname)s - %(message)s')

    # Initialize Google Cloud Logging client with service name
    gcp_client = gcp_logging.Client()
    gcp_handler = gcp_logging.handlers.CloudLoggingHandler(gcp_client)

    # Add the service name to the logs
    formatter = logging.Formatter(f'%(asctime)s -  %(levelname)s - {service_name} - %(message)s')
    gcp_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(gcp_handler)

if __name__ == "__main__":
    # Retrieve service name from environment variable, or default to 'unknown_service'
    setup_logging()
