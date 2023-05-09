from django.urls import path
from .views import APICreditView

urlpatterns = [
    # path('', APICreditView.as_view()),
    path('', APICreditView.as_view()),
]
