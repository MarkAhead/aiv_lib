from setuptools import setup, find_packages

setup(
    name="aiv_lib",
    version="0.1",
    packages=find_packages(),
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
        'whisperx @ git+https://github.com/m-bain/whisperx.git',
    ],
)
