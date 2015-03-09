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
    
import threading

def process_video(key_name):
    try:
        with open("videos_already_processed.txt", "a") as myfile:
            myfile.write(key_name+'\n')
        print 'starting instance for %s' % (key.name)
        #res = key.get_contents_to_filename(key.name) 
        #print res
        reservation = ec2conn.run_instances(settings['image_id'], instance_initiated_shutdown_behavior='terminate', instance_type='t2.micro', key_name=settings['key_name'], security_group_ids=[settings['security_group_id']])
        instance = reservation.instances[0]
        while True:
            try:
                if instance.update() == "running":
                    break
            except: 
                pass
            time.sleep(5)  # Run this in a green thread, ideally
        print instance.id, instance.ip_address
        # every 15 seconds try to login
        while True:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect((instance.ip_address, 22))
                print "Port 22 reachable"
                break
            except socket.error as e:
                print "Error on connect: %s" % e
            s.close()
            time.sleep(15)
        print 'ssh'
        # Originally I was making a AMI each update
        # By copying files to the new instance via SSH it becomes easier to update the video processing script
        os.system("scp -o StrictHostKeyChecking=no -i %s settings.json ubuntu@%s:~/settings.json" % (settings['pem_file'], instance.ip_address))
        os.system("scp -o StrictHostKeyChecking=no -i %s process_video.py ubuntu@%s:~/process_video.py" % (settings['pem_file'], instance.ip_address))
        os.system("ssh -o StrictHostKeyChecking=no -i %s ubuntu@%s 'python process_video.py %s True' &" % (settings['pem_file'], instance.ip_address, key_name))
    except:
        import sys, traceback
        print traceback.print_exc(file=sys.stdout)
    
threads = []
while True:
    for key in incoming_bucket.list():
        f = open('videos_already_processed.txt', 'r')
        files = f.read().split('\n')
        f.close()
        if not key.name in files: 
            t = threading.Thread(target=process_video, args=(key.name,))
            threads.append(t)
            t.start()
