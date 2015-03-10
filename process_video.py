#import boto
import json
with open('settings.json') as settings_file:    
    settings = json.load(settings_file)
from boto.s3.connection import S3Connection
s3conn = S3Connection(settings['aws_access_key_id'], settings["aws_secret_access_key"])
mybucket = s3conn.get_bucket(settings["incoming_bucket"])
import sys
video = sys.argv[1]
halt = True if sys.argv[2] == 'True' else False
import time
import os
from boto.s3.connection import S3Connection, Bucket, Key
b = Bucket(s3conn, settings["incoming_bucket"]) 

k = Key(b) 
k.key = video
k.get_contents_to_filename(video)

command = 'ffmpeg -threads 0 -i %s -crf 20 -preset ultrafast -vf "boxblur=6:4:cr=2:ar=2",format=yuv422p  -an overredacted_%s' % (video,video)
os.system(command)
b2 = Bucket(s3conn, settings["outgoing_bucket"])
k = b2.new_key(video)
k.set_contents_from_filename('overredacted_'+video)
youtube = settings['youtube']
command = 'python upload.py  --file="overredacted_%s" --title="%s" --description="%s" --keywords="%s" --category="22" --privacyStatus="%s"' % (video, video[:-4], youtube['description'], youtube['keywords'], youtube['privacy_status'])
os.system(command)
command = 'mkdir thumbs; ffmpeg -i overredacted_%s -vf fps=1/30 thumbs/img\%%04d.jpg' % (video)
os.system(command)
import boto
import boto.s3

import os.path
import sys

# Fill these in - you get them when you sign up for S3
AWS_ACCESS_KEY_ID = settings['aws_access_key_id']
AWS_ACCESS_KEY_SECRET = settings["aws_secret_access_key"]
# Fill in info on data to upload
# destination bucket name
bucket_name = settings["frames_bucket"]
# source directory
sourceDir = 'thumbs/'
# destination directory name (on s3)
destDir = video+'/'

#max size in bytes before uploading in parts. between 1 and 5 GB recommended
MAX_SIZE = 20 * 1000 * 1000
#size of parts when uploading in parts
PART_SIZE = 6 * 1000 * 1000

conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_ACCESS_KEY_SECRET)

bucket = conn.get_bucket(bucket_name)
bucket.set_acl('public-read')

uploadFileNames = []
for (sourceDir, dirname, filename) in os.walk(sourceDir):
    uploadFileNames.extend(filename)
    break

def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()

for filename in uploadFileNames:
    sourcepath = os.path.join(sourceDir + filename)
    destpath = os.path.join(destDir, filename)
    print 'Uploading %s to Amazon S3 bucket %s' % \
           (sourcepath, bucket_name)

    filesize = os.path.getsize(sourcepath)
    if filesize > MAX_SIZE:
        print "multipart upload"
        mp = bucket.initiate_multipart_upload(destpath)
        fp = open(sourcepath,'rb')
        fp_num = 0
        while (fp.tell() < filesize):
            fp_num += 1
            print "uploading part %i" %fp_num
            mp.upload_part_from_file(fp, fp_num, cb=percent_cb, num_cb=10, size=PART_SIZE)

        mp.complete_upload()

    else:
        print "singlepart upload"
        k = boto.s3.key.Key(bucket)
        k.key = destpath
        k.set_contents_from_filename(sourcepath,
                cb=percent_cb, num_cb=10)
        k.set_canned_acl('public-read')







os.system('rm -rf thumbs; rm *.mp4; rm *.mpg')
if settings['delete_raw_video_from_s3']:
    b.delete_key(k)
if halt:
    os.system('sudo halt')
