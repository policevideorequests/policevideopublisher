from django.db import models

class Word(models.Model):
    word = models.CharField(max_length=30, unique=True)
    safe = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.word