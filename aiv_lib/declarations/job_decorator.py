import time
import os
import sys
from datetime import datetime
import traceback

service_name = os.getenv("SERVICE_NAME", "S1")

def use_appopriate_time_format(time_in_seconds):
    """Format time duration in appropriate units."""
    if time_in_seconds < 60:
        return f"{time_in_seconds:.2f} seconds"
    elif time_in_seconds < 3600:
        return f"{time_in_seconds / 60:.2f} minutes"
    else:
        return f"{time_in_seconds / 3600:.2f} hours"

def log_environment_info():
    """Log relevant environment information for service debugging."""
    print(f"Service Environment Info:")
    print(f"  Service Name: {service_name}")
    print(f"  Python Version: {sys.version.split()[0]}")
    print(f"  Working Directory: {os.getcwd()}")
    
    # Log key environment variables (mask sensitive ones)
    relevant_env_vars = [
        'GOOGLE_APPLICATION_CREDENTIALS',
        'GOOGLE_CLOUD_PROJECT', 
        'FIREBASE_BUCKET',
        'ELEVENLABS_API_KEY',
        'SERVICE_NAME'
    ]
    
    print(f"  Environment Variables:")
    for env_var in relevant_env_vars:
        value = os.getenv(env_var)
        if value:
            # Mask sensitive values but show they exist
            if any(keyword in env_var.lower() for keyword in ['key', 'secret', 'token', 'password']):
                print(f"    {env_var}: [SET - {len(value)} chars]")
            else:
                print(f"    {env_var}: {value}")
        else:
            print(f"    {env_var}: [NOT SET]")
    
def job_decorator(func):
    """
    Enhanced job decorator with comprehensive logging for service lifecycle tracking.
    Provides structured logging for service startup, execution, success, and failure.
    """
    def wrapper(*args, **kwargs):
        # Service startup logging
        start_time = time.time()
        start_timestamp = datetime.now().isoformat()
        
        print(f"🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 {service_name} - {func.__name__} STARTING 🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩")
        print(f"Service Start Time: {start_timestamp}")
        
        # Log environment information for debugging
        log_environment_info()
        
        try:
            print(f"\n{service_name} - Executing {func.__name__}...")
            result = func(*args, **kwargs)

            # Service completion logging
            end_time = time.time()
            end_timestamp = datetime.now().isoformat()
            execution_duration = end_time - start_time

            print(f"\n=== {service_name} - {func.__name__} COMPLETED SUCCESSFULLY ===")
            print(f"Service End Time: {end_timestamp}")
            print(f"Total Execution Duration: {use_appopriate_time_format(execution_duration)}")
            print(f"Service Result: {result}")
            print(f"🛑🛑🛑🛑🛑🛑🛑🛑🛑🛑🛑🛑 {service_name} - {func.__name__} SUCCESS 🛑🛑🛑🛑🛑🛑🛑🛑🛑🛑🛑🛑")

            return result

        except Exception as e:
            # Service failure logging
            end_time = time.time()
            end_timestamp = datetime.now().isoformat()
            execution_duration = end_time - start_time
            
            print(f"\n❌❌❌ {service_name} - {func.__name__} FAILED ❌❌❌")
            print(f"Service Failure Time: {end_timestamp}")
            print(f"Execution Duration Before Failure: {use_appopriate_time_format(execution_duration)}")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print(f"Error Details:")
            
            # Print detailed traceback for debugging
            traceback.print_exc()
            
            print(f"💥💥💥💥💥💥💥💥💥💥💥💥 {service_name} - {func.__name__} FAILED 💥💥💥💥💥💥💥💥💥💥💥💥")
            
            # Re-raise the exception to ensure proper error handling upstream
            raise
            
    return wrapper