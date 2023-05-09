from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Project(models.Model):
    project_name = models.CharField(max_length=100)
    website = models.URLField(max_length=200, blank=True)
    about = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')

class KeywordSuggestionJob(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='keyword_suggestion_jobs')
    keywords = models.TextField()
    keyword_ideas = models.JSONField()


class Topicslist(models.Model):
    job = models.ForeignKey(KeywordSuggestionJob, on_delete=models.CASCADE)
    title = models.TextField()
    selected = models.BooleanField()

class Topic(models.Model):
    topic = models.ForeignKey(Topicslist, on_delete=models.CASCADE)
    blog = models.TextField()
    blog_titles = models.TextField()
    related_topics = models.TextField()
    meta_description = models.TextField()
    excerpt = models.TextField()
    microblogs = models.TextField()
    keywords = models.TextField()
    hashtags = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE,default=None)