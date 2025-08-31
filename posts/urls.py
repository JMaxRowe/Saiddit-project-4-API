from django.urls import path
from .views import PostListView, PostDetailView, PostRestoreView

urlpatterns=[
    path('', PostListView.as_view()),
    path('<int:pk>/', PostDetailView.as_view()),
    path('<int:pk>/restore/', PostRestoreView.as_view())
]
