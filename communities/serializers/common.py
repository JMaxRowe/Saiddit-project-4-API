from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from ..models import Community

class CommunitySerializer(ModelSerializer):
    creator = PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Community
        fields = "__all__"