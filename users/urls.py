from django.urls import path
from .views import UserRegistrationView,UserLoginView,UserLogoutView,UserTokenRefreshView, get_tokens
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', UserTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('social-login/', get_tokens, name='social_login'),
]

