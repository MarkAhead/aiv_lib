from setuptools import setup, find_packages

setup(
    name="aiv_lib",
    version="0.1",
    packages=find_packages(),
    # Consider adding a description, author, and other metadata fields
    # description="...",
    # author="...",
    # author_email="...",
    # url="...",
    
    install_requires=[
        'aiobotocore',
        'instagrapi',
        'requests',
        'flask',
        'Pillow',
        'moviepy',
        'openai',
        'elevenlabs',
        'pygame',
        'opencv-python',
        'firebase_admin',
        'boto3',
        'torchvision',
    ],
    
    # If there are any package data files, specify them
    # package_data={
    #     "": ["*.txt", "*.md"],
    # },
    
    # If there are any entry points or scripts, define them
    # entry_points={
    #     "console_scripts": [
    #         "my_script = my_package.module:function",
    #     ],
    # },
)
