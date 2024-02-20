import datetime
import os
from pathlib import Path
import sys


dir_name = get_config_value("base_folder")
SECOND_BRAIN_DIR = get_config_value("SECOND_BRAIN_DIR")


def find_and_replace():
    for path in Path(SECOND_BRAIN_DIR).rglob('*.md'):
        if "/bak/" in path.as_uri():
            continue
        with open(path, "r") as f:
            line = fp.readline()
            while line:
                if "![[" in line and ".png" in line:
                    print(line)


def get_daily_file_prefix():
    today = datetime.datetime.now()
    return today.strftime("%d_%m_%G")


def get_millisecond_file_prefix():
    today = datetime.datetime.now()
    epoch_time = int(today.timestamp() * 1000)  # Convert to milliseconds
    return str(epoch_time)

