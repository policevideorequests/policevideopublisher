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
youtube = settings['youtube']
# Videos with "cleared" in the filename get automatically uploaded to Youtube as is
if '_cleared' in video:
    command = 'python upload.py  --file="%s" --title="Clear w/ sound: %s" --description="%s" --keywords="%s" --category="22" --privacyStatus="%s"' % (video, video[:-4].replace('_cleared', ''), youtube['cleared_description'], youtube['keywords'], youtube['privacy_status'])
    os.system(command)
    
else:
    if settings["color"]:
        color = ''
    else:
        color = 'format=gray,' 
    #command = 'ffmpeg -threads 0 -i "%s" -crf 20 -preset ultrafast -vf %s"boxblur=%s:%s",format=yuv422p  -an "overredacted_%s"' % (video,color,settings["blurn"], settings["blurn"], video)
    command = 'ffmpeg -threads 0 -i "%s" -preset ultrafast -vf "edgedetect=low=0.25:high=0.5",scale=320:240,format=yuv422p  -an "overredacted_%s"' % (video, video[:-4]+'.mp4')
    #ffmpeg -i "takentoground.mp4" -strict -2  -vf "edgedetect=low=0.25:high=0.5",format=yuv422p takentoground_low_25_high_50.mp4
    os.system(command)
    os.system('rm *.wav; rm *.mp3')
    if not video.endswith('.mp4'):
        os.system('ffmpeg -threads 0 -i "%s" -strict -2 "%s"' % (video, video[:-4]+'.mp4'))
    #os.system('ffmpeg -threads 0 -i "%s" audio.mp3' % (video[:-4]+'.mp4'))
    #os.system('ffmpeg -threads 0 -i audio.mp3 audio.wav')
    os.system('ffmpeg -threads 0 -i "%s" -ac 1 audio.wav' % (video[:-4]+'.mp4'))
    # This code below was written by Chris Koss as a way to keep environmental sounds in audio while ensuring that information exempt from 
    # records act is not released
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy import fft, arange, ifft, io
    import wave
    import sys
    from scipy.io.wavfile import read,write



    #  using this to generate wav from mp4
    #
    #   ./ffmpeg -i axon.mp4 -ac 1 tricky.wav


    spf = wave.open('audio.wav','r')

    #Extract Raw Audio from Wav File
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, 'Int16')

    print spf.getparams()

    samplerate = spf.getparams()[2]

    INCR_SIZE = samplerate * spf.getparams()[0]

    if samplerate > 10000:
        # Old values
        bottom_bound_bottom = 0.005 * INCR_SIZE
        bottom_bound_top = 0.1 * INCR_SIZE

        mid_bound_bottom = 0.34 * INCR_SIZE
        mid_bound_top = 0.79 * INCR_SIZE

        top_bound_bottom = 0.9 * INCR_SIZE
        top_bound_top = 0.995 * INCR_SIZE
    else :
        bottom_bound_bottom = 0.03 * INCR_SIZE
        bottom_bound_top = 0.2 * INCR_SIZE

        mid_bound_bottom = 0.3 * INCR_SIZE
        mid_bound_top = 0.7 * INCR_SIZE

        top_bound_bottom = 0.8 * INCR_SIZE
        top_bound_top = 0.97 * INCR_SIZE


    start = 0
    end =  len(signal)

    #Using smaller chunk from the sample for ease of use

    #start = 2646000 + INCR_SIZE * 10
    #end = start + INCR_SIZE * 10
    #signal = signal[start:end]

    i = 0

    #print 'writing prefile'
    #write('pre.wav', INCR_SIZE, signal)

    while i < end - start:
        print i

        targ = signal[i:i + INCR_SIZE - 1]
        
        #plt.figure()
        #plt.plot(targ)
        #plt.savefig('out/' + str(i) + 'sig.png')
        Y=fft(targ)
        #print 'plot1'

        #plt.figure()
        #plt.plot(Y)
        #plt.savefig('out/' + str(i) + 'fft.png')
        
        Y[:bottom_bound_top] = 0
        Y[mid_bound_bottom:mid_bound_top] = 0

        Y[top_bound_bottom:top_bound_top] = 0
        
        #Y[86000:88000] = 0    


        
        #plt.figure()
        #plt.plot(Y)
        #plt.savefig('out/' + str(i) + 'fft2.png')

        signal[i:i + INCR_SIZE - 1] = ifft(Y)
        
        i += INCR_SIZE


    print 'writing file'    
    write('out.wav', INCR_SIZE, signal)
    os.system('ffmpeg -threads 0 -i "overredacted_%s" -i out.wav -strict -2 -b:a 32k "with_sound2_overredacted_%s"' % (video[:-4]+'.mp4', video[:-4]+'.mp4'))
    #os.system('ffmpeg -threads 0 -i "overredacted_%s" -i out.wav -strict -2 "with_sound2_overredacted_%s"' % (video[:-4]+'.mp4', video[:-4]+'.mp4'))
    #b2 = Bucket(s3conn, settings["outgoing_bucket"])
    #k = b2.new_key(video) 
    #k.set_contents_from_filename('overredacted_'+video)
    import re
    if re.search('AXON \w+ Video \d+\-\d+\-\d+ \d+', video) or re.search('\d+\@\d+', video):
        title = 'Over-redacted preview of '+video[:-4]
    else:
        import time
        title = 'Over-redacted preview of a SPD BodyWornVideo processed on %s' % (time.strftime("%b %d %H:%M:%S"))
    command = 'python upload.py  --file="with_sound2_overredacted_%s" --title="%s" --description="%s" --keywords="%s" --category="22" --privacyStatus="%s"' % (video[:-4]+'.mp4', title, youtube['description'], youtube['keywords'], youtube['privacy_status'])
    os.system(command)
    command = 'mkdir thumbs; ffmpeg -i "overredacted_%s" -vf fps=1/30 thumbs/img\%%04d.jpg' % (video)
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
print 'test if delete raw video'
if settings['delete_raw_video_from_s3']:
    print 'deleting raw video'
    b = Bucket(s3conn, settings["incoming_bucket"]) 

    k = Key(b) 
    k.key = video
    b.delete_key(k)
if halt:
    os.system('sudo halt')
