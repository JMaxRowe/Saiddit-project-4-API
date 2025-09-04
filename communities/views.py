from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from .models import Community
from .serializers.common import CommunitySerializer

class CommunityListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        qs = Community.objects.all()
        return Response(CommunitySerializer(qs, many=True, context={'request': request}).data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)
        serializer = CommunitySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        community = serializer.save(creator=request.user)
        community.members.add(request.user)
        return Response(CommunitySerializer(community, context={'request': request}).data, status=201)

class CommunityDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Community, pk=pk)

    def get(self, request, pk):
        community = self.get_object(pk)
        return Response(CommunitySerializer(community, context={'request': request}).data)

    def put(self, request, pk):
        community = self.get_object(pk)
        if community.creator != request.user:
            return Response({"detail": "Forbidden"}, status=403)
        serializer = CommunitySerializer(community, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CommunitySerializer(community, context={'request': request}).data)

    def delete(self, request, pk):
        community = self.get_object(pk)
        if community.creator != request.user:
            return Response({"detail": "Forbidden"}, status=403)
        community.delete()
        return Response(status=204)
    

class CommunityJoinView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        community = get_object_or_404(Community, pk=pk)
        community.members.add(request.user)
        return Response({"status": "joined"})

class CommunityLeaveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        community = get_object_or_404(Community, pk=pk)
        community.members.remove(request.user)
        return Response({"status": "left"})

class CommunityRestoreView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        community = get_object_or_404(Community, pk=pk)
        if request.user != community.creator:
            return Response({"detail": "Forbidden"}, status=403)
        community.restore()
        return Response({"status": "restored"}, status=200)