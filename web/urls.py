from django.urls import re_path as url
from . import views
from django.urls import path
from .views import usersubscription,usersubscription_expry,membershipview,payment_order_create

urlpatterns = [
    path('membership/', membershipview.as_view, name='membership'),

    path('membershipview/',  membershipview.as_view(), name='membershipview'), 
    path('subscription/', usersubscription.as_view(), name='subscription'), #get current plan
    #path('subscription_expiry/', usersubscription_expry.as_view(), name='subscription_expiry'), #get current plan expiry


    path('payment_order_create/', payment_order_create.as_view(), name='payment_order_create'), #xreate plan order 
    url('webhooks/stripe/', views.call_back_url, name='payment'), #payment confirmation
]