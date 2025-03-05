import time
import os
service_name = os.getenv("SERVICE_NAME", "S1")

def use_appopriate_time_format(time_in_seconds):
    if time_in_seconds < 60:
        return f"{time_in_seconds} seconds"
    elif time_in_seconds < 3600:
        return f"{time_in_seconds / 60} minutes"
    
def job_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(f"🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 {service_name} - {func.__name__} 🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩")
        result = func(*args, **kwargs)
        print("total time taken: ", use_appopriate_time_format(time.time() - start_time))
        print(f"🛑🛑🛑🛑🛑🛑🛑🛑🛑🛑🛑🛑 {service_name} - {func.__name__} 🛑🛑🛑🛑🛑🛑🛑🛑🛑🛑🛑🛑")
        return result
    return wrapper