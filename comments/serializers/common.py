from rest_framework.serializers import ModelSerializer, ValidationError, IntegerField
from ..models import Comment
from users.serializers.common import OwnerSerializer

class CommentSerializer(ModelSerializer):
    score = IntegerField(read_only=True)
    replies_count = IntegerField(read_only=True)
    commenter = OwnerSerializer(read_only=True)

    class Meta:
        model=Comment
        fields = ["id", "body", "created_at", "commenter", "post", "parent_comment", "is_deleted", "score"]
        read_only_fields = ["id", "created_at", "commenter", "is_deleted", "score"]

    def validate_parent_comment(self, value):
        post_id = self.initial_data.get("post")
        if value and post_id and value.post_id != int(post_id):
            raise ValidationError("Parent comment must belong to the same post.")
        return value