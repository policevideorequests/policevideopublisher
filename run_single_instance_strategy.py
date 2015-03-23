"""1. Police department uploads the video to S3 bucket for incoming videos
2. As video are saved in the bucket a threaded script creates an EC2 instance per item in bucket 
3. The threaded script sends a command over SSH with the argument being the key name of the video on the S3 bucket
4. The called script then saves the video locally, processes it, saves it in the S3 bucket for finished videos, and halts/terminates itself
5. A threaded script uploads processed videos to endpoint such as Youtube as the processed videos are saved 
6. The threaded script generates a series of images every 30 seconds of the video"""
# Load our settings.json file which contains AWS keys, bucket names, key_name, security_group_id
import json
with open('settings.json') as settings_file:    
    settings = json.load(settings_file)
from boto.s3.connection import S3Connection
s3conn = S3Connection(settings['aws_access_key_id'], settings['aws_secret_access_key'])
incoming_bucket = s3conn.get_bucket(settings['incoming_bucket'])
import boto.ec2
ec2conn = boto.ec2.connect_to_region(settings['region'], aws_access_key_id=settings['aws_access_key_id'], aws_secret_access_key=settings['aws_secret_access_key'])
import time
import os
import os.path
if not os.path.isfile('videos_already_processed.txt'):
    os.system('touch videos_already_processed.txt') 
    
import time
while True:
    import json
    # Allows one to change the settings without restarting the script
    with open('settings.json') as settings_file:    
        settings = json.load(settings_file)
    for key in incoming_bucket.list():
        f = open('videos_already_processed.txt', 'r')
        files = f.read().split('\n')
        f.close()
        if not key.name in files: 
            with open("videos_already_processed.txt", "a") as myfile:
                myfile.write(key.name+'\n')
            os.system('python process_video.py "%s" False' % (key.name))
    time.sleep(60)
