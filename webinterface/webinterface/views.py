from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
import os
import json
import re
from models import Word

def get_settings():
    f = open(os.path.join(os.getcwd(), '../settings.json'))
    settings = f.read()
    return json.loads(settings)

def home(request):
    settings = get_settings()
    return render_to_response('home.html', {'system_name': settings['system_name']})
    
def is_logged_in(request):
    return HttpResponse(request.user.is_authenticated())
    
    
@login_required
def test_artibury_ffmpeg_options(request):
    import os
    print os.getcwd()
    os.system('rm test_videos/overredacted_*; rm test_videos/frames/*')
    videos = [name for name in os.listdir("test_videos") if name.endswith(".mp4")]
    color = True if request.GET['color'] == 'true' else False
    blurn = int(request.GET['blurn'])
    if color:
        color = ''
    else:
        color = 'format=gray,'
    for video in videos:
        command = 'ffmpeg -threads 0 -i test_videos/%s -crf 20 -preset ultrafast -vf %s"boxblur=%s:%s",format=yuv422p  -an test_videos/overredacted_%s' % (video,color,blurn,blurn,video)
        fcommand = command
        os.system(command)
        command = 'ffmpeg -i test_videos/overredacted_%s -vf fps=1/30 test_videos/frames/%s_img\%%04d.jpg' % (video, video)
        #os.system(command)
        #command = 'ffmpeg -i test_videos/overredacted_%s -vf fps=1/30 test_videos/frames/n%s_img\%%04d.jpg' % (video, video)
        os.system(command)
    overredacted_frames = ['/test_frames/' + item for item in sorted(os.listdir("test_videos/frames"))]
    print color, blurn, fcommand
    return HttpResponse(json.dumps(overredacted_frames), content_type="application/json")

@login_required
def test_ffmpeg_options(request):
    import os
    print os.getcwd()
    overredacted_frames = ['/test_frames/' + item for item in sorted(os.listdir("test_videos/frames")) if 'color_'+request.GET['color']+'_blurn_'+str(request.GET['blurn'])+'_' in item]
    
    return HttpResponse(json.dumps(overredacted_frames), content_type="application/json")
    
@login_required
def current_settings(request):
    f = open(os.path.join(os.getcwd(), '../settings.json'))
    settings = f.read()
    return HttpResponse(settings, content_type="application/json")   

def is_capitalized(word):
    if not word:
        return False
    else:
        return word[0].isupper()    
    
def get_words():
    f = open('/usr/share/dict/american-english', 'r')
    words = f.read().split('\n') 
    f.close()
    some_proper_nouns = [word for word in words if is_capitalized(word)]        
    words = [word for word in words if not is_capitalized(word)] # eliminate proper nouns
    words += ['I', 'RMS', 'Seattle', '911'] 
    return words    
    
@login_required
def change_settings(request):
    import time
    timestr = time.strftime("%Y%m%d-%H%M%S")
    # backup the current settings
    os.system('mkdir ../settings_backups; cp ../settings.json ../settings_backups/settings_%s.json' % (timestr))
    f = open(os.path.join(os.getcwd(), '../settings.json'))
    settings = json.loads(f.read())
    f.close()
    new_settings = json.loads(request.POST['new_settings'])
    settings.update(new_settings)
    f = open(os.path.join(os.getcwd(), '../settings.json'), 'w')
    settings = f.write(json.dumps(settings))
    f.close()
    return HttpResponse('done')
    
@login_required
def test_frames(request, filename):
    import magic
    mime = magic.Magic(mime=True)
    
    filepath = os.path.join(os.getcwd(), 'test_videos/frames/'+filename)
    print 'filepath', filepath
    image_data = open(filepath, "rb").read()
    return HttpResponse(image_data, content_type=mime.from_file(filepath))
    
def login(request):
    from django.contrib.auth import authenticate, login
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponse('valid')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("invalid")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("invalid")
            
@login_required
def logout(request):
    from django.contrib.auth import logout
    logout(request)    
    return HttpResponse('Logged out')
    
def get_random_id():
    import random
    return ''.join(random.choice('0123456789ABCDEF') for i in range(16))    
   
@login_required   
def broken_report(request):
    random_id = get_random_id()
    f = open('../reports/test.txt', 'r')
    the_report = f.read()
    f = open('/usr/share/dict/american-english', 'r')
    words = f.read().split('\n') 
    def is_capitalized(word):
        if not word:
            return False
        else:
            return word[0].isupper()
    some_proper_nouns = [word for word in words if is_capitalized(word)]        
    words = [word for word in words if not is_capitalized(word)] # eliminate proper nouns
    words += ['I']
    f.close()    
    report_words = the_report.split(' ')
    overredacted_report = []
    for word in report_words:
        if word.strip() not in words:
            overredacted_report.append('*redacted*')
        else:
            overredacted_report.append(word)
    overredacted_report = ' '.join(overredacted_report)
    return HttpResponse(overredacted_report, content_type="text/plain")
    
def extract_narrative(report):
    preview = report
    lines = preview.split('\n')
    preview = lines[lines.index('15 INITIAL INCIDENT DESCRIPTION / NARRATIVE:')+1:lines.index('I hereby declare (certify) under penalty of perjury under the laws of the')]
    if preview[0].startswith('['):
        preview[0] = preview[0][1:]
    unneccessaries = ['Page', 'For: ', 'PATROL', 'SEATTLE POLICE DEPARTMENT', 'GENERAL OFFENSE HARDCOPY', 'PUBLIC DISCLOSURE RELEASE COPY', 'GO#', 'LAW DEPT BY FOLLOW-UP UNIT', ']']
    for unneccessary in unneccessaries:
        preview = [line.strip() for line in preview if not line.startswith(unneccessary)]
    import re
    preview = [line.strip() for line in preview if not re.search('[A-Z0-9]+\-[A-Z0-9]+ [A-Z0-9]+\-[A-Z0-9]+', line)]
    preview = [line.strip() for line in preview if not re.search('\d+\-\d+ [A-Z]+ [A-Z\-]+', line)]
    preview = '\n'.join(preview)
    paragraphs = preview.split('\n\n')
    print 'parahraphs', len(paragraphs)
    paragraphs = [paragraph.replace('\n', ' ') for paragraph in paragraphs]
    preview = '\n\n'.join(paragraphs)
    preview = preview.replace('\n'*5, ' ')
    preview = preview.replace('\n'*4, ' ')
    preview = preview.replace('\n'*3, ' ')
    preview = preview.strip()
    return preview

def get_redacted_words(narrative):
    from models import Word
    import re
    safe_words = [w.word for w in Word.objects.filter(safe=True)]
    
    redacted_words = []
    narrative_words = filter(None, re.split("[ \n]+", narrative))
    for word in narrative_words:
        if word not in safe_words:
            redacted_words.append(word)
    
    redacted_words = sorted(list(set(redacted_words)))
    return redacted_words

def remove_punctuation(word):
    return word.strip('.?!,":\'\#\(\)\/').replace("'s", '')
    
def is_recent_date(word):
    if not re.search('^\d+[/\-]\d+[/\-]\d+$', remove_punctuation(word)):
        return False
    try:
        from dateutil.parser import parse
        import datetime
        a = datetime.datetime.now()
        b = parse(word)
        c = a - b
        if c.days < 60:
            return True
        else:
            return False
    except:
        import sys, traceback
        traceback.print_exc(file=sys.stdout)
        return False    
    
def is_call_sign(word):
    if re.search('^[0-9][A-Z][0-9]$', word):
        return True
    elif re.search('^\d\-\w+\-\d$', word):
        return True
    else:
        return False    


        
def mark_sentence_words_for_redaction(sentence):
    safe_words = [w.word for w in Word.objects.filter(safe=True)]
    unsafe_words = [w.word for w in Word.objects.filter(safe=False)]
    s = []
    narrative_words = sentence.split(' ')    
    for i, word in enumerate(narrative_words):
        if re.search('^[A-Z]\.$', word): # person's middle initial 
            s.append('<span class="unsafe">%s</span>.' % (word[0]))
        elif re.search('^\d{2}\"$', word): # measurement
            s.append(word)
        elif re.search('^[A-Z]/[A-Z]$', word):
            s.append(word)
        elif re.search('^\$[\d\.]+$', word):
            s.append(word)
        elif re.search('^\d{4}$', word) and narrative_words[i+1] == 'hours': # to deal with 1150 hours
            s.append(word)
        elif re.search("^\w+/[\w']+$", remove_punctuation(word)):
            w1, w2 = word.split('/')
            if not w1 in safe_words:
                w1 = '<span class="unsafe">%s</span>' % (w1)
            if not w2 in safe_words:
                if w2.endswith("'s"):
                    w2 = '<span class="unsafe">%s</span>\'s' % (w2[:-2])
                else:
                    #w2 = '<span class="unsafe">%s</span>' % (w2)
                    w2 = re.sub('[\w\d/\-]+', '<span class="unsafe" title="not in dictionary">%s</span>' % (remove_punctuation(w2)), w2)
            s.append('%s/%s' % (w1, w2))
        elif re.search('^\w+,\w+$', remove_punctuation(word)):
            w1, w2 = word.split(',')
            if not w1 in safe_words:
                w1 = '<span class="unsafe">%s</span>' % (w1)
            if not w2 in safe_words:
                #w2 = '<span class="unsafe">%s</span>' % (w2)
                w2 = re.sub('[\w\d/\-]+', '<span class="unsafe" title="not in dictionary">%s</span>' % (remove_punctuation(w2)), w2)
            s.append('%s,%s' % (w1, w2))
        elif i == 0 or re.search('^"[A-Z]', word): # if quote in front of capitalized word like "Pulled a gun on him."
            if remove_punctuation(word) not in safe_words and remove_punctuation(word).lower() not in safe_words or remove_punctuation(word) in unsafe_words:
                #s.append('<span class="unsafe" title="unsafe first word of sentence">%s</span>' % (word))
                if "'s" in word:
                    s.append(re.sub('[\w\d/\-\:]+', '<span class="unsafe" title="unsafe first word of sentence">%s</span>\'s' % (remove_punctuation(word)), word.replace("'s", '')))
                else:
                    s.append(re.sub('[\w\d\-]+', '<span class="unsafe" title="unsafe first word of sentence">%s</span>' % (remove_punctuation(word)), word))
            else:
                s.append('<span title="first word of sentence">%s</span>' % (word))
        elif re.search('^\d{2}\:\d{2}$', remove_punctuation(word)):
            s.append('<span title="time">%s</span>' % (word))
        elif is_recent_date(word):
            s.append('<span title="is recent date">%s</span>' % (word))
        elif is_call_sign(word):
            s.append('<span title="call sign">%s</span>' % (word))
        else:
            if remove_punctuation(word) not in safe_words and not '-' in word:
                if "'s" in word:
                    s.append(re.sub('[\w\d/\-\:]+', '<span class="unsafe" title="not in dictionary">%s</span>\'s' % (remove_punctuation(word)), word.replace("'s", '')))
                else:
                    s.append(re.sub('[\w\d/\-\']+', '<span class="unsafe" title="not in dictionary">%s</span>' % (remove_punctuation(word)), word))
            elif '-' in word: # deal with words like anti-harassment order
                safe = True
                for w in word.split('-'):
                    if not remove_punctuation(w) in safe_words:
                        safe = False
                if safe:
                    s.append(word)
                else:
                    s.append(re.sub('[\w\d/\-]+', '<span class="unsafe" title="word with dash">%s</span>' % (remove_punctuation(word)), word))
            else:
                s.append(word)
    return ' '.join(s) 
    
def mark_words_for_redaction(narrative):
    if re.search('^[A-Z\d\s,\-\.]+$', narrative):
        return '<span title="every letter is capitalized">%s</span>' % (narrative)
    import nltk.data

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    safe_words = [w.word for w in Word.objects.filter(safe=True)]
    s = []
    narrative_words = filter(None, re.split("[ \n]+", narrative))
    sentences = tokenizer.tokenize(narrative)
    return ' '.join([mark_sentence_words_for_redaction(sentence) for sentence in sentences]) 
    
@login_required
def mark_word_as_safe(request):
    try:
        word = Word(word=request.POST['word'], safe=True)
        word.save()
    except:
        word = Word.objects.get(word=request.POST['word'])
        word.safe = True
        word.save()
    return HttpResponse('')        
    
@login_required
def overredact_reports(request):
    print 'good'
    print request.FILES
    os.system('mkdir ../reports/')
    print 'saving'
    random_id = get_random_id()
    f = open('../reports/%s.pdf' % (random_id), 'w')
    f.write(request.FILES['file'].read())
    f.close()
    os.system('pdf2txt.py ../reports/%s.pdf > ../reports/%s.txt' % (random_id, random_id))
    os.system('rm ../reports/%s.pdf' % (random_id))
    f = open('../reports/%s.txt' % (random_id))
    os.system('rm ../reports/%s.txt' % (random_id))
    preview = f.read()
    
    preview = extract_narrative(preview).strip(']')
    
    redacted_words = get_redacted_words(preview)
    paragraphs = preview.split('\n\n')
    processed_paragraphs = []
    for paragraph in paragraphs:
        processed_paragraphs.append(mark_words_for_redaction(paragraph))
    preview = '\n\n'.join(processed_paragraphs)
    # Given a PDF and email address: convert the PDF to text, overredact it, and email the overredacted text version to the supplied email address 
    #return HttpResponse(json.dumps({'message': 'File uploaded successfully!', 'preview': preview.replace('\n', '<br/>'), 'redacted_words': redacted_words}), content_type="application/json")
    return HttpResponse(json.dumps({'message': 'File uploaded successfully!', 'preview': preview.replace('\n', '<br/>')}), content_type="application/json")
    
@login_required 
def email_report(request):
    settings = get_settings()
    import smtplib
    recipient = request.POST['to']

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    session.login(settings["email_username"], settings["email_password"])
    email_subject = "Police report narrative you requested"
    body_of_email = request.POST['body']
    
    headers = "\r\n".join(["from: Seattle Police <spdnews@seattle.gov>",
                       "subject: " + email_subject,
                       "to: " + request.POST['to'],
                       "mime-version: 1.0",
                       "content-type: text/html"])

    # body_of_email can be plaintext or html!                    
    content = headers + "\r\n\r\n" + body_of_email
    session.sendmail("timacbackup", request.POST['to'], content)
    session.quit()
    return HttpResponse('done')