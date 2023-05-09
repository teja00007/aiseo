from django.urls import path
from .views import ProjectList, ProjectDetail, KeywordSuggestionJobList, KeywordSuggestionJobDetail, TopicList, TopicDetail, wordpress_push

urlpatterns = [
    path('', ProjectList.as_view(), name='project-list'),
    path('<int:pk>/', ProjectDetail.as_view(), name='project-detail'),
    path('<int:project_id>/jobs/', KeywordSuggestionJobList.as_view(), name='keyword-suggestion-job-list'),
    path('jobs/<int:pk>/', KeywordSuggestionJobDetail.as_view(), name='keyword-suggestion-job-detail'),
    path('topicslist/<int:job_id>', TopicList.as_view(), name='topic-list'),
    path('blog/<int:Topic_id>/', TopicDetail.as_view(), name='topic-detail'),
    path('wordpress/', wordpress_push.as_view(), name='wordpress'),
]