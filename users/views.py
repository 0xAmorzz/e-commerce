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
from .tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .models import User
from django.conf import settings


# Create your views here.

class AccountActivationView(APIView):
    permission_classes = []
    authentication_classes = []
    
    def get(self, request, uidb64, token):
        user = User
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except:
            user = None
        
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid activation link'}, status=status.HTTP_400_BAD_REQUEST)


def activateEmail(request, user, to_email):
    mail_subject = f'NEXA Email Verification for {user.first_name} {user.last_name}'
    message = render_to_string('users/email/verification_email.html', {
        'user': user,
        'domain': os.getenv('FRONTEND_URL') or '127.0.0.1:8000',
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http',
    })
    email = EmailMessage(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
    email.content_subtype = "html"
    email.send()


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
            response.set_cookie(key="access_token", value=str(refresh.access_token), httponly=not settings.DEBUG, secure= not settings.DEBUG, samesite='Strict')
            response.set_cookie(key="refresh_token", value=str(refresh), httponly=not settings.DEBUG, secure=not settings.DEBUG, samesite='Strict')
            activateEmail(request, user, user.email)
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
            response.set_cookie(key="access_token", value=str(refresh.access_token), httponly=not settings.DEBUG, secure=not settings.DEBUG, samesite='Strict')
            response.set_cookie(key="refresh_token", value=str(refresh), httponly=not settings.DEBUG, secure=not settings.DEBUG, samesite='Strict')
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# reminder to make it get
class UserLogoutView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]               

    @extend_schema(request=None, responses={200: 'User logged out successfully', 400: 'Bad Request'})

    def get(self, request):
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
            response.set_cookie(key="access_token", value=new_access_token, httponly=not settings.DEBUG, secure=not settings.DEBUG, samesite='Strict')
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={200: 'Password changed successfully', 400: 'Bad Request'})
    def post(self,request):
        user = request.user
        old_password = request.data['old_password']
        new_password = request.data['new_password']
        if user.check_password(old_password):
            if old_password == new_password:
                return Response({'error': 'New password cannot be the same as the old password'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)

@login_required
def get_tokens(request):
    refresh = RefreshToken.for_user(request.user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:8000')
    response = redirect(frontend_url)
    response.set_cookie(key="access_token", value=access_token, httponly=not settings.DEBUG, secure=not settings.DEBUG, samesite='Strict')
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=not settings.DEBUG, secure=not settings.DEBUG, samesite='Strict')
    return response