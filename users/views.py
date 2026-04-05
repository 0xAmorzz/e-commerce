from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.views import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes




# Create your views here.

class UserRegistrationView(APIView):
    @extend_schema(request=UserRegistrationSerializer, responses={201: UserRegistrationSerializer})

    # post method to handle user registeration
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh),'access': str(refresh.access_token)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def get_tokens(request):
    access_token = request.session.get('access_token')
    refresh_token = request.session.get('refresh_token')
    return Response({'access_token': access_token, 'refresh_token': refresh_token}, status=status.HTTP_200_OK)
