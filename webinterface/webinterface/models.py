from django.db import models
from django.contrib.auth.models import User

class Word(models.Model):
    word = models.CharField(max_length=30, unique=True)
    safe = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.word
        
class RedactionEvent(models.Model):
    report_filename = models.CharField(max_length=50)
    user = models.ForeignKey(User)
    datetime = models.DateTimeField(auto_now_add=True)
    word = models.CharField(max_length=20)
    is_marked = models.BooleanField(default=False)
    is_wordlist_modified = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s, %s, %s, %s, %s, %s" % (self.report_filename, self.user.username, self.datetime, self.word, self.is_marked, self.is_wordlist_modified)
    
class ProcessingLog(models.Model):
    report_filename = models.CharField(max_length=50)
    user = models.ForeignKey(User)
    start_time = models.DateTimeField(auto_now_add=True)
    stop_time = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return "%s, %s, %s, %s" % (self.report_filename, self.user.username, self.start_time, self.stop_time)