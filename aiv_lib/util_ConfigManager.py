import os
import shutil
from aiv_lib.util_gcp_secret_manager import get_secret_value
import configparser

def print_expected_env_variables():
    print(""" 
    ------------------------------------------------------------
    Expected environment variables:
    ------------------------------------------------------------
    """)
    print("which_config: " + str(os.environ.get('which_config')))
    print("platform_key: " + str(os.environ.get('platform_key')))
    print("GOOGLE_APPLICATION_CREDENTIALS: " + str(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))
    print("PYTHONPATH: " + str(os.environ.get('PYTHONPATH')))
    print("MODEL_PATH: " + str(os.environ.get('MODEL_PATH')))
    print("--------------------------------------------")

def load_config():
    print_expected_env_variables()
    # Get the secret key from the environment variable
    which_config_key = os.environ.get('which_config')
    if not which_config_key:
        raise SystemExit('which_config environment variable not found.')
    
    # Fetch the secret value
    try:
        config_value = get_secret_value(which_config_key)
        if not config_value or not config_value.strip():
            raise ValueError(f"Secret '{which_config_key}' is empty or contains only whitespace")
    except Exception as e:
        raise SystemExit(f'Failed to fetch secret "{which_config_key}": {e}')
    
    # Parse the config value using configparser
    config = configparser.ConfigParser()
    try:
        config.read_string(config_value)
    except configparser.Error as e:
        raise SystemExit(f'Failed to parse configuration from secret "{which_config_key}": {e}')
    except Exception as e:
        raise SystemExit(f'Unexpected error parsing configuration: {e}')

    # Validate that DEFAULT section exists
    if 'DEFAULT' not in config:
        raise SystemExit(f'Configuration missing required DEFAULT section. Available sections: {list(config.sections())}')

    # Get the platform key from the environment variable
    platform_key = os.environ.get('platform_key', 'DEFAULT')
    print(f"platform_key: {platform_key}")
    
    # Handle platform-specific configuration with better error handling
    platform_config = {}
    if platform_key != 'DEFAULT' and platform_key in config:
        platform_config = dict(config[platform_key])
    elif platform_key != 'DEFAULT':
        print(f"Warning: Platform '{platform_key}' not found in configuration. Available sections: {list(config.sections())}")
    
    # Merge configurations with explicit dict conversion to handle sparse data
    try:
        default_config = dict(config['DEFAULT'])
        # Convert all keys to lowercase for consistency
        default_config = {key.lower(): value for key, value in default_config.items()}
        
        platform_config_normalized = {}
        if platform_config:
            platform_config_normalized = {key.lower(): value for key, value in platform_config.items()}
        
        final_config = {**default_config, **platform_config_normalized}
        
        # Validate that we have some configuration values
        if not final_config:
            raise SystemExit('Configuration is empty after parsing')
            
        return final_config
    except Exception as e:
        raise SystemExit(f'Failed to merge configuration sections: {e}')

def get_config_value(key):
    if config_manager is None:
        raise SystemExit('Configuration manager not initialized')
    
    # Normalize key to lowercase for consistent access
    normalized_key = key.lower()
    value = config_manager.get(normalized_key)
    if value is None:
        print(f"Warning: Configuration key '{key}' (normalized: '{normalized_key}') not found. Available keys: {list(config_manager.keys())}")
    return value

def create_output_folder(name : str):
    output_folder = get_config_value('output_folder')
    output_folder = os.path.join(output_folder, name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    return output_folder
        
def empty_and_delete_directory(dir_path):
    # Check if the directory exists
    if os.path.exists(dir_path):
        # Remove all files and subdirectories in the directory
        shutil.rmtree(dir_path)
        print(f"The directory '{dir_path}' has been emptied and deleted.")
    else:
        print(f"The directory '{dir_path}' does not exist.")

def set_openai_api_key():
    try:
        api_key = get_config_value("openai_api_key")
        if api_key and api_key.strip():
            os.environ["OPENAI_API_KEY"] = api_key
            print("OpenAI API key set successfully")
        else:
            print("Warning: OpenAI API key not found or empty in configuration")
    except Exception as e:
        print(f"Warning: Failed to set OpenAI API key: {e}")
        # Don't raise an exception here as this might not be critical for all services

def get_firestore_client():
    import firebase_admin
    from firebase_admin import firestore
    firebase_admin.initialize_app()
    
    # Get a Firestore client
    db = firestore.client()
    
    return db

config_manager = None

def get_temp_folder():
    return create_output_folder("temp")

def initialize():
    global config_manager
    try:
        config_manager = load_config()
        print(f"Configuration loaded successfully with {len(config_manager)} keys")
        set_openai_api_key()
    except SystemExit:
        # Re-raise SystemExit to maintain current behavior
        raise
    except Exception as e:
        print(f"Critical error during configuration initialization: {e}")
        raise SystemExit(f'Configuration initialization failed: {e}')

# Initialize with error handling
try:
    initialize()
except SystemExit as e:
    print(f"Configuration initialization failed: {e}")
    # Re-raise to maintain existing behavior
    raise

def debug_configuration():
    """Debug function to print configuration structure and identify issues"""
    if config_manager is None:
        print("ERROR: Configuration manager not initialized")
        return
    
    print("=== Configuration Debug Information ===")
    print(f"Total configuration keys: {len(config_manager)}")
    print(f"Configuration keys (normalized to lowercase): {sorted(config_manager.keys())}")
    
    # Check for common required keys (normalize to lowercase)
    required_keys = ['output_folder', 'openai_api_key']
    missing_keys = []
    empty_keys = []
    
    for key in required_keys:
        value = config_manager.get(key.lower())  # Use lowercase for lookup
        if value is None:
            missing_keys.append(key)
        elif not str(value).strip():
            empty_keys.append(key)
    
    if missing_keys:
        print(f"Missing required keys: {missing_keys}")
    if empty_keys:
        print(f"Empty required keys: {empty_keys}")
    
    # Show sample of configuration (mask sensitive values)
    print("\nSample configuration values:")
    for key, value in sorted(config_manager.items())[:10]:  # Show first 10 keys
        if any(sensitive in key.lower() for sensitive in ['key', 'secret', 'token', 'password']):
            display_value = f"[MASKED - {len(str(value))} chars]" if value else "[EMPTY]"
        else:
            display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
        print(f"  {key}: {display_value}")
    
    print("=== End Configuration Debug ===")
    print("\nNote: All configuration keys are normalized to lowercase for consistent access.")

if __name__ == "__main__":
    debug_configuration()
    print(get_config_value("output_folder"))

def get_config_value_with_fallback(key):
    """
    Enhanced version of get_config_value that tries both original case and lowercase.
    This provides backwards compatibility during the transition period.
    """
    if config_manager is None:
        raise SystemExit('Configuration manager not initialized')
    
    # First try lowercase (new standard)
    normalized_key = key.lower()
    value = config_manager.get(normalized_key)
    
    if value is not None:
        return value
    
    # If not found, try original case for backwards compatibility
    value = config_manager.get(key)
    if value is not None:
        print(f"Warning: Found '{key}' with original case. Please update to use lowercase: '{normalized_key}'")
        return value
    
    print(f"Warning: Configuration key '{key}' not found in any case. Available keys: {list(config_manager.keys())}")
    return None

def show_key_normalization_mapping():
    """Helper function to show how keys were normalized"""
    if config_manager is None:
        print("Configuration manager not initialized")
        return
    
    print("=== Key Normalization Mapping ===")
    # This would show the before/after if we had the original data
    # For now, just show current normalized keys
    print("Current normalized keys:")
    for key in sorted(config_manager.keys()):
        print(f"  {key}")
    print("=== End Mapping ===")

# Backwards compatibility alias
def get_config_value_legacy(key):
    """Legacy function - use get_config_value instead"""
    print(f"Warning: get_config_value_legacy is deprecated. Use get_config_value('{key.lower()}') instead.")
    return get_config_value_with_fallback(key)
