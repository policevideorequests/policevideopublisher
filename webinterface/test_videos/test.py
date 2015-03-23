import os
os.system('rm overredacted_*; rm frames/*')
videos = [name for name in os.listdir(".") if name.endswith(".mp4")]
color = True
blurn = 9
# filenames *n*_color_true_blurn_*n*
for color in [True, False]:
    for blurn in range(0, 21):
		for video in videos:
			
			command = 'ffmpeg -threads 0 -i %s -crf 20 -preset ultrafast -vf %s"boxblur=%s:%s",format=yuv422p  -an overredacted_color_%s_blurn_%s_%s' % (video, '' if color else 'format=gray,', blurn, blurn, str(color).lower(), blurn, video)
			os.system(command)
			command = 'mkdir thumbs; ffmpeg -i overredacted_color_%s_blurn_%s_%s -vf fps=1/30 frames/overredacted_color_%s_blurn_%s_%s_img\%%04d.jpg' % (str(color).lower(), blurn, video, str(color).lower(), blurn, video)
			os.system(command)
    