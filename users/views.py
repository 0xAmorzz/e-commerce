from urllib import response
from .authentication import CookieJWTAuthentication
from django.shortcuts import redirect
import os
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.views import extend_schema
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required




# Create your views here.

class UserRegistrationView(APIView):
    permission_classes = []
    authentication_classes = []
    @extend_schema(request=UserRegistrationSerializer, responses={201: UserRegistrationSerializer})

    # post method to handle user registeration
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            response = Response({'refresh': str(refresh),'access': str(refresh.access_token)}, status=status.HTTP_201_CREATED)
            response.set_cookie(key="access_token", value=str(refresh.access_token), httponly=True, secure=True, samesite='Strict')
            response.set_cookie(key="refresh_token", value=str(refresh), httponly=True, secure=True, samesite='Strict')
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = []
    authentication_classes = []
    @extend_schema(request=UserLoginSerializer, responses={200: UserLoginSerializer, 400: 'Invalid email or password'})

    # post method to handle user login
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            response = Response({'refresh': str(refresh),'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
            response.set_cookie(key="access_token", value=str(refresh.access_token), httponly=True, secure=True, samesite='Strict')
            response.set_cookie(key="refresh_token", value=str(refresh), httponly=True, secure=True, samesite='Strict')
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]               

    @extend_schema(request=None, responses={200: 'User logged out successfully', 400: 'Bad Request'})

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            print(22)
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({'error': str(e)},status=status.HTTP_400_BAD_REQUEST)
        response = Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

class UserTokenRefreshView(APIView):
    permission_classes = []
    authentication_classes = []

    @extend_schema(request=None, responses={200: 'Access token refreshed successfully', 400: 'bad request'})

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token is None:
            return Response({'error' : 'Refresh token is not provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)
            response = Response({'message': 'Access token refreshed successfully', 'access_token': new_access_token}, status=status.HTTP_200_OK)
            response.set_cookie(key="access_token", value=new_access_token, httponly=True, secure=True, samesite='Strict')
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



@login_required
def get_tokens(request):
    refresh = RefreshToken.for_user(request.user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:8000')
    response = redirect(frontend_url)
    response.set_cookie(key="access_token", value=access_token, httponly=False, secure=False, samesite='Strict')
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=False, secure=False, samesite='Strict')
    return response