from rest_framework import serializers
from .models import Project, KeywordSuggestionJob, Topicslist, Topic

class ProjectSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField()
    website = serializers.CharField()
    about = serializers.CharField()
    class Meta:
        model = Project
        fields = ['id','project_name','website','about']


class KeywordSuggestionJobSerializer(serializers.ModelSerializer):
    keywords = serializers.CharField()
    keyword_ideas = serializers.JSONField()
    class Meta:
        model = KeywordSuggestionJob
        fields = ['id','keywords','keyword_ideas']

class TopicslistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topicslist
        fields = ['id','job', 'title']

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"

class blogSerializer(serializers.ModelSerializer):
    topic_id = serializers.IntegerField()
    url = serializers.CharField()
    class Meta:
        model = Topic
        fields = ['topic_id','url']