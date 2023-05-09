from django.contrib import admin
from .models import Membership, UserMembership, Subscription, PayHistory

admin.site.register(UserMembership)
admin.site.register(Membership)
admin.site.register(Subscription)
admin.site.register(PayHistory)
