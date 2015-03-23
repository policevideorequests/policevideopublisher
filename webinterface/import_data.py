import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webinterface.settings")

from webinterface.models import Word

def is_capitalized(word):
    if not word:
        return False
    else:
        return word[0].isupper()
        
f = open('/usr/share/dict/american-english', 'r')
words = [w for w in f.read().split('\n') if w]
for word in words:
    if is_capitalized(word):
        w = Word(word=word, safe=False)
    else:
        w = Word(word=word, safe=True)
    w.save()
