from rest_framework import serializers
from .models import APICredit

class APICreditSerializer(serializers.ModelSerializer):

    class Meta:
        model = APICredit
        fields = ['user', 'credits']
