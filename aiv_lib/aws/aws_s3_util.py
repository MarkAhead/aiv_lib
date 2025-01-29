#!/usr/bin/env python
# coding: utf-8

import boto3
from boto3 import Session


def get_s3_client():
    session = Session(profile_name="default")
    client = boto3.client('s3')
    return client


def download_s3_object(bucket, key, output_file):
    client = get_s3_client()
    with open(output_file, 'wb') as data:
        client.download_fileobj(bucket, key, data)
    print("Audio File downloaded successfully at " + output_file)

def upload_s3_object(bucket, key, file_path):
    client = get_s3_client()
    client.upload_file(file_path, bucket, key)
    print("File uploaded successfully to s3 at " + bucket + "/" + key)
    