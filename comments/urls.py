from django.urls import path
from .views import CommentListView, CommentDetailView, CommentRestoreView

urlpatterns=[
    path('', CommentListView.as_view()),
    path('<int:pk>/', CommentDetailView.as_view()),
    path('<int:pk>/restore/', CommentRestoreView.as_view())
]
