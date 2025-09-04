from django.urls import path, include
from communities.views import (CommunityListCreateView, CommunityDetailView, CommunityJoinView, CommunityLeaveView, CommunityRestoreView)

urlpatterns = [
    path('', CommunityListCreateView.as_view()),
    path('<int:pk>/', CommunityDetailView.as_view()),
    path('<int:pk>/join/', CommunityJoinView.as_view()),
    path('<int:pk>/leave/', CommunityLeaveView.as_view()),
    path('<int:pk>/restore/', CommunityRestoreView.as_view()),
]