from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import APICredit
from .serializers import APICreditSerializer
from web.models import Membership
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
User = get_user_model()

class APICreditView(APIView):
    serializer_class = APICreditSerializer
    
    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
    
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        payload = jwt.decode(token, settings.SECRET_KEY,algorithms='HS256')
        user = User.objects.get(id=payload['user_id'])
        #import pdb;pdb.set_trace()
        api_credits = APICredit.objects.filter(user=user)
        serializer = APICreditSerializer(api_credits, many=True)
        return Response(serializer.data)
