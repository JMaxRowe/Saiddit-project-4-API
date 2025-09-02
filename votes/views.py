from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Vote
from .serializers.common import VoteSerializer
from rest_framework.exceptions import NotFound, PermissionDenied
from django.contrib.contenttypes.models import ContentType


# Create your views here.
class VoteView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serialized_vote = VoteSerializer(data=request.data)
        if serialized_vote.is_valid():
            content_type = serialized_vote.validated_data["content_type"]
            object_id = serialized_vote.validated_data["object_id"]
            value = serialized_vote.validated_data["value"]
            vote, created = Vote.objects.update_or_create(
                voter=request.user,
                content_type=content_type,
                object_id=object_id,
                defaults={"value": value}
            )
            return Response({
                "post": ContentType.objects.get_by_natural_key('posts','post').id,
                "comment": ContentType.objects.get_by_natural_key('comments','comment').id,
            })
        return Response(serialized_vote.errors, status=400)
    
    def delete(self, request):
        content_type_id = request.data.get("content_type")
        object_id = request.data.get("object_id")

        try:
            vote = Vote.objects.get(
                voter=request.user,
                content_type_id=content_type_id,
                object_id=object_id
            )
            vote.delete()
            return Response({"status": "vote removed"}, status=204)
        except Vote.DoesNotExist:
            return Response({"error": "vote not found"}, status=404)