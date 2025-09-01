from rest_framework.serializers import ModelSerializer, IntegerField
from ..models import Post
from users.serializers.common import OwnerSerializer
from communities.serializers.common import CommunitySerializer

class PostSerializer(ModelSerializer):
    score = IntegerField(read_only=True)
    comments_count = IntegerField(read_only=True)
    poster = OwnerSerializer(read_only=True)
    community = CommunitySerializer(read_only=True)

    class Meta:
        model=Post
        fields="__all__"