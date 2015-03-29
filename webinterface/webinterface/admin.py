from django.contrib import admin
from models import Word, RedactionEvent, ProcessingLog
# search_fields = ['user__email']
class WordAdmin(admin.ModelAdmin):
    search_fields = ['=word']
admin.site.register(Word, WordAdmin)
admin.site.register(RedactionEvent)
admin.site.register(ProcessingLog)