import uuid
from datetime import datetime, timedelta

import jwt
import pytz
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .models import User
from .permissions import IsOwnerOrAdmin
from .serializers import (EmailVerificationSerializer,
                          PasswordResetConfirmSerializer,
                          PasswordResetRequestSerializer, TokenInfoSerializer,
                          TokenRefreshSerializer, UserLoginSerializer,
                          UserRegisterSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    def generate_email_verification_token(self, user):
        payload = {
            'user_id': user.id,
            'exp': datetime.now(pytz.UTC) + timedelta(days=7),
            'type': 'email_verification',
            'jti': str(uuid.uuid4())
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    def generate_password_reset_token(self, user):
        payload = {
            'user_id': user.id,
            'exp': datetime.now(pytz.UTC) + timedelta(hours=24),
            'type': 'password_reset',
            'jti': str(uuid.uuid4())
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    @swagger_auto_schema(
        request_body=UserRegisterSerializer,
        responses={
            201: UserSerializer,
            400: 'Bad Request'
        },
        operation_description="Register a new user",
        security=[]
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate verification token
            token = self.generate_email_verification_token(user)
            
            # Send verification email
            verification_url = (
                f"{settings.FRONTEND_URL}/verify-email?token={token}"
            )
            subject = "Verify your email address"
            message = (
                f"Please verify your email by clicking on the link: "
                f"{verification_url}"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            return Response({
                'user': UserSerializer(user).data,
                'message': 'User registered successfully. Please verify your email.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=EmailVerificationSerializer,
        responses={
            200: 'Email verified successfully',
            400: 'Bad Request',
            401: 'Invalid or expired token'
        },
        operation_description="Verify user email with token",
        security=[]
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_email(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            
            try:
                # Decode the token
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=['HS256']
                )
                
                if payload['type'] != 'email_verification':
                    return Response(
                        {'error': 'Invalid token type'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Get the user and activate the account
                user = User.objects.get(id=payload['user_id'])
                user.is_active = True
                user.save()
                
                # Generate auth tokens
                tokens = self.get_tokens_for_user(user)
                
                return Response({
                    'message': 'Email verified successfully',
                    'user': UserSerializer(user).data,
                    'tokens': tokens
                })
            
            except jwt.ExpiredSignatureError:
                return Response(
                    {'error': 'Verification link has expired'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            except (jwt.DecodeError, User.DoesNotExist):
                return Response(
                    {'error': 'Invalid verification token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={
            200: UserSerializer,
            401: 'Invalid credentials'
        },
        operation_description="Login with username and password",
        security=[]
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    return Response(
                        {'error': 'Please verify your email before logging in'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                
                tokens = self.get_tokens_for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'tokens': tokens,
                    'message': 'Login successful'
                })
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=PasswordResetRequestSerializer,
        responses={
            200: 'Password reset email sent',
            400: 'Bad Request',
            404: 'User not found'
        },
        operation_description="Request password reset email",
        security=[]
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def request_password_reset(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Generate reset token
                token = self.generate_password_reset_token(user)
                
                # Send reset email
                reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
                subject = "Reset your password"
                message = f"To reset your password, click on the link: {reset_url}"
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                
                return Response({
                    'message': 'Password reset email sent'
                })
            
            except User.DoesNotExist:
                # We still return success to prevent email enumeration attacks
                return Response({
                    'message': 'Password reset email sent'
                })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: 'Password reset successful',
            400: 'Bad Request',
            401: 'Invalid or expired token'
        },
        operation_description="Reset password with token",
        security=[]
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def reset_password_confirm(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                # Decode the token
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=['HS256']
                )
                
                if payload['type'] != 'password_reset':
                    return Response(
                        {'error': 'Invalid token type'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Get the user and set the new password
                user = User.objects.get(id=payload['user_id'])
                user.set_password(new_password)
                user.save()
                
                return Response({
                    'message': 'Password reset successful'
                })
            
            except jwt.ExpiredSignatureError:
                return Response(
                    {'error': 'Password reset link has expired'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            except (jwt.DecodeError, User.DoesNotExist):
                return Response(
                    {'error': 'Invalid password reset token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=TokenRefreshSerializer,
        responses={
            200: openapi.Response(
                description="Token refresh successful",
                examples={
                    "application/json": {
                        "access": "new_access_token",
                        "refresh": "new_refresh_token"
                    }
                }
            ),
            401: 'Invalid refresh token'
        },
        operation_description="Refresh access token using refresh token",
        security=[]
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def refresh_token(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            try:
                refresh_token = RefreshToken(serializer.validated_data['refresh'])
                return Response({
                    'access': str(refresh_token.access_token),
                    'refresh': str(refresh_token)
                })
            except TokenError:
                return Response(
                    {'error': 'Invalid refresh token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=TokenInfoSerializer,
        responses={
            200: openapi.Response(
                description="Token information",
                examples={
                    "application/json": {
                        "expires_at": "2024-02-23T12:00:00Z",
                        "remaining_time": "55 minutes"
                    }
                }
            ),
            401: 'Invalid token'
        },
        operation_description="Get token expiration information",
        security=[]
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def token_info(self, request):
        serializer = TokenInfoSerializer(data=request.data)
        if serializer.is_valid():
            try:
                token = AccessToken(serializer.validated_data['token'])
                exp_timestamp = token['exp']
                exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=pytz.UTC)
                now = datetime.now(pytz.UTC)
                remaining_time = exp_datetime - now

                return Response({
                    'expires_at': exp_datetime.isoformat(),
                    'remaining_time': str(remaining_time).split('.')[0],
                    'is_valid': True
                })
            except TokenError:
                return Response(
                    {'error': 'Invalid token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
