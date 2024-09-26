import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta
import json
from .util_ConfigManager import get_config_value

database_file  = get_config_value('resources_folder') + get_config_value('database_file')
job_execution_config_path = get_config_value('job_execution_config_path')


# Load job configurations from the JSON file
with open(job_execution_config_path, "r") as config_file:
    job_configs = json.load(config_file)["jobs"]

sql_create_job_execution_table = '''
    CREATE TABLE IF NOT EXISTS job_executions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_path TEXT,
        execution_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(database_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_job_execution_table():
    conn = create_connection()
    if conn is not None:
        create_table(conn, sql_create_job_execution_table)
        print("job_executions table created successfully")
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

def get_execution_count_for_job(job_path):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            end_time = datetime.now()
            start_time = end_time - timedelta(days=1)

            cursor.execute('''
                SELECT COUNT(*) FROM job_executions
                WHERE job_path = ? AND execution_time >= ? AND execution_time <= ?
            ''', (job_path, start_time, end_time))

            execution_count = cursor.fetchone()[0]
            return execution_count

        except Error as e:
            print(e)
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")


def get_jobs_to_execute():
    jobs_to_execute = []

    for job_config in job_configs:
        job_path = job_config["job_path"]
        max_executions_per_day = job_config["max_executions_per_day"]
        execution_count = get_execution_count_for_job(job_path)

        if execution_count < max_executions_per_day:
            jobs_to_execute.append(job_path)

    return jobs_to_execute

def update_job_count(job_paths):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            for job_path in job_paths:
                cursor.execute('''
                    INSERT INTO job_executions (job_path) VALUES (?)
                ''', (job_path,))
            conn.commit()
        except Error as e:
            print(e)
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    create_job_execution_table()

    # Example usage:
    jobs_to_execute = get_jobs_to_execute(job_configs)
    
    if jobs_to_execute:
        print("Jobs to execute:", jobs_to_execute)
        # Execute the jobs here using os.system or any other method
