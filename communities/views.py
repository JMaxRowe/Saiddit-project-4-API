from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from rest_framework import viewsets, permissions, status
from .models import Community
from .serializers.common import CommunitySerializer

class CommunityViewSets(viewsets.ModelViewSet):
    
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        community = serializer.save(creator=self.request.user)
        community.members.add(self.request.user)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        community = self.get_object()
        community.members.add(request.user)
        return Response({"status": "joined"})
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        community = self.get_object()
        community.members.remove(request.user)
        return Response({"status": "left"})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def restore(self, request, pk=None):
        community = self.get_object()
        if not (request.user == community.creator):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        community.restore()
        return Response({"status": "restored"}, status=status.HTTP_200_OK)