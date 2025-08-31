from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommunityViewSets

router = DefaultRouter()
router.register(r'', CommunityViewSets, basename='community')

urlpatterns = [
    path('', include(router.urls)),
]