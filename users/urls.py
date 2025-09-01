from django.urls import path
from .views import SignUpView
from rest_framework_simplejwt.views import (TokenObtainPairView)
from .serializers.tokens import TokenSerializer

urlpatterns = [
    path('sign-up/', SignUpView.as_view()),
    path('sign-in/', TokenObtainPairView.as_view())
]