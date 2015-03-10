# policevideopublisher

This is a tool for police departments to automatically generate and publish previews of body camera videos. 
The objective is to allow police departments to be as transparent as possible while protecting the privacy of citizens.

## Process:

1. Videos are uploaded to the Amazon Web Services S3 bucket for incoming videos
2. Depending on the strategy used: use one instance, use one instance per video, or a hybrid approach a script checks for new videos in the S3 incoming bucket 
3. The videos are processed via FFMPEG
4. Thumbnails of every 30 seconds of each processed video are generated and saved in the S3 bucket for frames
5. The processed video is uploaded to Youtube

### Process of generating previews:

In order to ensure the identities of juveniles and witnesses/victims who request non-disclosure at the time of the incident are protected more is redacted than normally would when responding to a formal records request because there is no reliable auto-redaction tool available yet.
