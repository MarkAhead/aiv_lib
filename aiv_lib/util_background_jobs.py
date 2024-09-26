import random
import threading
import os
import time

# Create a lock object
lock = threading.Lock()
random.seed(time.time())

    
def runInBackgroundContinuouslyWithInterval(interval, function):
    threading.Timer(interval, runInBackgroundContinuouslyWithInterval, [interval, function]).start()
    # Try to acquire the lock before running the function
    if not lock.acquire(blocking=False):
        print(f"Another thread is already running {function.__name__}, so skipping this execution.")
        return
    try:
        function()
    finally:
        # Make sure to release the lock after the function is done
        lock.release()

def background_job_random(lower_limit, upper_limit, function):
    # Generate a random interval between the lower and upper limits (inclusive)
    interval = random.uniform(lower_limit, upper_limit)
    
    # Schedule the function to run again after the random interval
    threading.Timer(interval, background_job_random, [lower_limit, upper_limit, function]).start()
    
    # Try to acquire the lock before running the function
    if not lock.acquire(blocking=False):
        print(f"Another thread is already running {function.__name__}, so skipping this execution.")
        return
    
    try:
        function()
    finally:
        # Make sure to release the lock after the function is done
        lock.release()


# Example usage
def example_function():
    print("Function is running at", time.strftime("%H:%M:%S"))

if __name__ == "__main__":
    background_job_random(10, 20, example_function)
    
    