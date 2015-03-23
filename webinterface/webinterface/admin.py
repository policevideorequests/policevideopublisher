from django.contrib import admin
from models import Word
# search_fields = ['user__email']
class WordAdmin(admin.ModelAdmin):
    search_fields = ['=word']
admin.site.register(Word, WordAdmin)