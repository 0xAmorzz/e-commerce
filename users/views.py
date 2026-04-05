from urllib import response

from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, UserLoginSerializer
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
            response = Response({'refresh': str(refresh),'access': str(refresh.access_token)}, status=status.HTTP_201_OK)
            response.set_cookie(key="access_token", value=str(refresh.access_token), httponly=True, secure=True, samesite='Strict')
            response.set_cookie(key="refresh_token", value=str(refresh), httponly=True, secure=True, samesite='Strict')
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
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
    permission_classes = [IsAuthenticated]
    @extend_schema(request=None, responses={200: 'User logged out successfully', 400: 'Bad Request'})

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({'error': str(e)},status=status.HTTP_400_BAD_REQUEST)
        response = Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

class UserTokenRefreshView(APIView):
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





@api_view(['GET'])
def get_tokens(request):
    access_token = request.session.get('access_token')
    refresh_token = request.session.get('refresh_token')
    return Response({'access_token': access_token, 'refresh_token': refresh_token}, status=status.HTTP_200_OK)
