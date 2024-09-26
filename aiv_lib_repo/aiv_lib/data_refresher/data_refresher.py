# info_updater/scheduler.py

import schedule
import time
import threading

from .storage import Storage


class DataRefresher:
    def __init__(self):
        self.storage =  Storage()

    def schedule_fetching(self, key, fetching_logic, refresh_duration_minutes):
        """
        Schedules a periodic update for the given key using the provided fetching logic.

        Args:
            key (str): The key to identify the data to update.
            fetching_logic (callable): The function that fetches the data.
            refresh_duration_minutes (int): The interval in minutes to refresh the data.
        """
        def job():
            data = fetching_logic()
            self.storage.add_data(key, data)

        schedule.every(refresh_duration_minutes).minutes.do(job)

    def start(self):
        """
        Starts the scheduler in a background thread.
        """
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(500)

        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True  # Allows the thread to exit when the main program exits
        scheduler_thread.start()
        
    def get_data(self, key):
        """
        Retrieves the latest data associated with the given key.

        Args:
            key (str): The key to identify the stored data.

        Returns:
            The latest data associated with the key, or None if the key is not found.
        """
        return self.storage.get_data(key)