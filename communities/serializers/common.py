from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, SerializerMethodField
from ..models import Community

class CommunitySerializer(ModelSerializer):
    creator = PrimaryKeyRelatedField(read_only=True)
    is_member = SerializerMethodField()

    class Meta:
        model = Community
        fields = "__all__"

    def get_is_member(self, obj):
        user = self.context['request'].user
        return obj.members.filter(id=user.id).exists()