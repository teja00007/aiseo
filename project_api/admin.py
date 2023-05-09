from django.contrib import admin

# Register your models here.
from .models import KeywordSuggestionJob,Project,Topicslist,Topic

admin.site.register(Project)
admin.site.register(KeywordSuggestionJob)
admin.site.register(Topicslist)
admin.site.register(Topic)