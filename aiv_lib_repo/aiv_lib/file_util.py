import os
import shutil

# Function to copy contents
def copy_contents(src, dst):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)  # For Python 3.8 and above
        else:
            shutil.copy2(s, d)
            
            
            
f