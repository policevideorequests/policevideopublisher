from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
import os
import json
import re
from models import Word, ProcessingLog, RedactionEvent

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
    
def extract_narrative(report):
    preview = report
    lines = preview.split('\n')
    if '15 INITIAL INCIDENT DESCRIPTION / NARRATIVE:' in preview:
        preview = lines[lines.index('15 INITIAL INCIDENT DESCRIPTION / NARRATIVE:') + 1: lines.index('I hereby declare (certify) under penalty of perjury under the laws of the')]
    elif 'OFFICER NARATIVE' in preview:
        preview = lines[lines.index('OFFICER NARATIVE') + 1: lines.index('I hereby declare (certify) under penalty of perjury under the laws of the')]
    
    else:
        preview = lines[1:lines.index('I hereby declare (certify) under penalty of perjury under the laws of the')]

    if preview[0].startswith('['):
        preview[0] = preview[0][1:]
    unneccessaries = ['Page', 'For: ', 'PATROL', 'CLEARANCE', 'NARRATIVE', 'OFFICER NARRATIVE', 'NARRATIVE TEXT HARDCOPY', 'SEATTLE POLICE DEPARTMENT', 'GENERAL OFFENSE HARDCOPY', 'PUBLIC DISCLOSURE RELEASE COPY', 'GO#', 'LAW DEPT BY FOLLOW-UP UNIT', ']']
    for unneccessary in unneccessaries:
        preview = [line.strip() for line in preview if not line.startswith(unneccessary)]
    import re
    preview = [line.strip() for line in preview if not re.search('[A-Z0-9]+\-[A-Z0-9]+ [A-Z0-9]+\-[A-Z0-9]+', line)]
    preview = [line.strip() for line in preview if not re.search('\d+\-\d+ [A-Z]+ [A-Z\-]+', line)]
    preview = [line.strip() for line in preview if not re.search('^[A-Z\-]+$', line.strip())]
    preview = [line.strip() for line in preview if not line.startswith('Author:')]
    preview = [line.strip() for line in preview if not line.startswith('Related date:')]
    
    preview = '\n'.join(preview)
    paragraphs = preview.split('\n\n')
    #print 'parahraphs', len(paragraphs)
    paragraphs = [paragraph.replace('\n', ' ') for paragraph in paragraphs]
    preview = '\n\n'.join(paragraphs)
    preview = preview.replace('\n'*5, ' ')
    preview = preview.replace('\n'*4, ' ')
    preview = preview.replace('\n'*3, ' ')
    preview = preview.strip()
    preview = preview.replace('Sgt.', 'Sgt')
    return preview

def get_redacted_words(narrative):
    from models import Word
    import re
    safe_words = [w.word for w in Word.objects.filter(safe=True)]
    
    redacted_words = []
    narrative_words = filter(None, re.split("[ \n]+", narrative))
    for word in narrative_words:
        if word not in safe_words:
            redacted_words.append('<span class="safe">%s</span>' % (word))
    
    redacted_words = sorted(list(set(redacted_words)))
    return redacted_words

def remove_punctuation(word):
    return word.strip('.?!,":\'\#\(\)\{\}\/;').replace("'s", '')
    
def is_recent_date(word): # objective is to ensure birthdays are not released
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
    if re.search('^\d+[A-Za-z]+\d+$', word):
        return True
    elif re.search('^\d\-[A-Za-z]+\-\d+$', word): # 2W11
        return True
    else:
        return False    

def is_count(word, next_word):
    if re.search('^[\d\.]+$', remove_punctuation(word)) and remove_punctuation(next_word).endswith('s'):
        return True
    else:
        return False    
        
def is_persons_initial(word):
    return True if re.search('^[\w]\.$', word) else False
        
def is_measurement(word):
    return re.search('^\d{2}\"$', word)

def is_age(word, next_word):
    if re.search('^\d+$', word):
        if next_word.startswith('year'):
            return True
        else:
            return False
    else:
        return False
        
def is_officer(word, prev_prev_word, prev_word):
    abbreviations = ['Officer', 'officer', 'Off.', 'Off','OFC', 'Ofc', 'SGT', 'Sgt', 'LT', 'Lt', 'CPT', 'Cpt', 'Sgt.']
    if remove_punctuation(prev_word) in abbreviations or remove_punctuation(prev_prev_word) in abbreviations:
        if is_capitalized(word) or re.search('^\#\d+$', remove_punctuation(word)): # Officer #3830
            return True
        else:
            return False
    else:
        return False

def is_ordinal(word, next_word):
    if re.search('^\d+(th|nd|rd)$', remove_punctuation(word.lower())):
        return True
    elif re.search('^\d+$', word) and remove_punctuation(next_word.lower()) in ['th', 'nd', 'rd']:
        return True
    else:
        return False    
        
def is_street_name(word, prev_word, next_word):
    if is_capitalized(word):
        t = False
        address_initials = ['S', 'S.', 'St.', 'AVE', 'AV', 'Av', 'Alley', 'Al']
        if prev_word in address_initials or next_word in address_initials:
            return True
        else:
            return False
    elif re.search('^\d+AV$', word):
        return True
        
    else:
        return False
    
def is_block(word, next_word):
    if re.search('^\d+$', word) and next_word in ['block']:
        return True
    else:
        return False    
    
def is_ssn(word):
    if re.search('\d{3}\-\d{2}\-\d{4}', word):
        return True
    else:
        return False    
    
def is_building_number(word, next_word):
    if re.search('^\d+$', word) and (is_capitalized(next_word) or re.search('^\dAV$', next_word)):
        return True
    else:
        return False
    
def is_dollar(word):
    if re.search('^\$[\d\.]+$', remove_punctuation(word)):
        return True
    else:
        return False    
    
def mark_sentence_words_for_redaction(sentence, safe_words, unsafe_words):
    
    s = []
    narrative_words = sentence.split(' ')   
    next_word = ''
        
    for i, word in enumerate(narrative_words):
        next_word = ''
        prev_word = ''
        prev_prev_word = ''
        try:
            next_word = narrative_words[i+1]
        except:
            pass
        try:
            prev_word = narrative_words[i-1]
        except:
            pass
        try:
            prev_prev_word = narrative_words[i-2]
        except:
            pass
        if is_ssn(remove_punctuation(word)):
            s.append('<span class="unsafe" title="social security number">XXX</span>-<span class="unsafe" title="social security number">XX</span>-<span class="unsafe" title="social security number">XXXX</span>')
        elif is_persons_initial(word): # person's middle initial 
            s.append('<span class="unsafe">%s</span>.' % (word[0]))
        elif is_count(word, next_word):
            s.append('<span class="safe">%s</span>' % (word))
        elif is_street_name(word, prev_word, next_word):
            s.append('<span class="safe">%s</span>' % (word))
        elif is_block(word, next_word):
            s.append('<span class="safe">%s</span>' % (word))
        elif is_building_number(word, next_word):
            s.append(word[:-2]+'<span class="unsafe">'+word[-2:]+'</span>')
        elif is_officer(word, prev_prev_word, prev_word):
            s.append('<span class="safe">%s</span>' % (word))
        elif is_measurement(word): # measurement
            s.append('<span class="safe">%s</span>' % (word))
        elif is_age(word, next_word):
            s.append('<span class="safe">%s</span>' % (word))
        elif is_ordinal(word, next_word):
            s.append('<span class="safe">%s</span>' % (word))
        elif re.search('^[A-Z]/[A-Z]$', remove_punctuation(word)):
            s.append('<span class="safe">%s</span>' % (word))
        elif is_dollar(word):
            s.append('<span class="safe">%s</span>' % (word))
        elif re.search('^\d{4}$', word) and remove_punctuation(next_word) in ['hours', 'hrs']: # to deal with 1150 hours
            s.append('<span class="safe">%s</span>' % (word))
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
        elif is_call_sign(remove_punctuation(word)):
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
                    s.append('<span class="safe">%s</span>' % (word))
                else:
                    s.append(re.sub('[\w\d/\-]+', '<span class="unsafe" title="word with dash">%s</span>' % (remove_punctuation(word)), word))
            else:
                s.append('<span class="safe">%s</span>' % (word))
    return ' '.join(s) 
    
def mark_words_for_redaction(narrative, safe_words, unsafe_words):
    print 'start'
    if re.search('^[A-Z\d\s,\-\.]+$', narrative):
        return '<span title="every letter is capitalized">%s</span>' % (narrative)
    import nltk.data

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    safe_words = [w.word for w in Word.objects.filter(safe=True)]
    s = []
    narrative_words = filter(None, re.split("[ \n]+", narrative))
    sentences = tokenizer.tokenize(narrative)
    print 'done'
    return ' '.join([mark_sentence_words_for_redaction(sentence, safe_words, unsafe_words) for sentence in sentences]) 
    
@login_required
def mark_word(request, the_type):
    safe = True if the_type == 'safe' else False
    is_modify = True if request.POST.get('modify') == 'true' else False
    if is_modify:
        try:
            word = Word(word=request.POST['word'], safe=safe)
            word.save()
        except:
            word = Word.objects.get(word=request.POST['word'])
            word.safe = True
            word.save()
    redaction_event = RedactionEvent(report_filename=request.POST['report_filename'], user=request.user, word=request.POST['word'], is_marked=not safe, is_wordlist_modified=is_modify)
    redaction_event.save()
    return HttpResponse('')        
    
@login_required
def overredact_reports(request):
    os.system('mkdir ../reports/')
    random_id = get_random_id()
    with open('../reports/history.txt', 'a') as historyfile:
        historyfile.write('\n'+request.FILES['file'].name+'\n')
        
    f = open('../reports/%s.pdf' % (random_id), 'w')
    f.write(request.FILES['file'].read())
    f.close()
    os.system('pdf2txt.py ../reports/%s.pdf > ../reports/%s.txt' % (random_id, random_id))
    #os.system('rm ../reports/%s.pdf' % (random_id))
    f = open('../reports/%s.txt' % (random_id))
    #os.system('rm ../reports/%s.txt' % (random_id))
    preview = f.read()
    
    preview = extract_narrative(preview).strip(']')
    
    redacted_words = get_redacted_words(preview)
    paragraphs = preview.split('\n\n')
    processed_paragraphs = []
    print '# of paragraphs: %s' % (len(paragraphs))
    safe_words = [w.word for w in Word.objects.filter(safe=True)]
    unsafe_words = [w.word for w in Word.objects.filter(safe=False)]
    processed_paragraphs = [mark_words_for_redaction(paragraph, safe_words, unsafe_words) for paragraph in paragraphs]
    preview = '\n\n'.join(processed_paragraphs)
    processing_log = ProcessingLog(report_filename=request.FILES['file'].name, user=request.user)
    processing_log.save()
    processing_id = processing_log.id
    return HttpResponse(json.dumps({'processing_id': processing_id, 'report_filename': request.FILES['file'].name, 'message': 'File uploaded successfully!', 'preview': preview.replace('\n', '<br/>')}), content_type="application/json")
    
@login_required 
def email_report(request):
    try:
        processing_log = ProcessingLog(id=request.POST['processing_id'])
        from datetime import datetime    
        processing_log.stop_time = datetime.now()
        processing_log.save()
    except:
        pass
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
                       "X-Bcc: policevideorequests@gmail.com", 
                       
                       "mime-version: 1.0",
                       "content-type: text/html"])

    # body_of_email can be plaintext or html!                    
    content = headers + "\r\n\r\n" + body_of_email
    session.sendmail("timacbackup", request.POST['to'], content)
    session.quit()
    return HttpResponse('done')