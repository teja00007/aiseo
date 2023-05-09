from rest_framework import serializers
from .models import Membership,UserSetting,PayHistory,UserMembership,Subscription

from rest_framework import serializers

class PayHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PayHistory
        fields = "__all__"

class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields =  "__all__"

class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = "__all__"

class UserMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMembership
        fields = "__all__"

class MembershippaymentSerializer(serializers.ModelSerializer):
    plan = serializers.CharField(max_length=255, min_length=3)

    class Meta:
        model = Membership
        fields = ['plan']

class SubscriptionSerializer(serializers.ModelSerializer):
  class Meta:
    model = Subscription
    fields = "__all__"