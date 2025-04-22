from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/',
         UserViewSet.as_view({'post': 'register'}),
         name='register'),
    path('auth/login/',
         UserViewSet.as_view({'post': 'login'}),
         name='login'),
    path('auth/verify-email/',
         UserViewSet.as_view({'post': 'verify_email'}),
         name='verify-email'),
    path('auth/request-password-reset/',
         UserViewSet.as_view({'post': 'request_password_reset'}),
         name='request-password-reset'),
    path('auth/reset-password-confirm/',
         UserViewSet.as_view({'post': 'reset_password_confirm'}),
         name='reset-password-confirm'),
    path('auth/refresh-token/',
         UserViewSet.as_view({'post': 'refresh_token'}),
         name='refresh-token'),
    path('auth/token-info/',
         UserViewSet.as_view({'post': 'token_info'}),
         name='token-info'),
]
