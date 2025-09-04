from rest_framework.serializers import ModelSerializer, ValidationError, IntegerField, SerializerMethodField
from ..models import Comment
from users.serializers.common import OwnerSerializer
from django.contrib.contenttypes.models import ContentType


class CommentSerializer(ModelSerializer):
    score = IntegerField(read_only=True)
    replies_count = IntegerField(read_only=True)
    commenter = OwnerSerializer(read_only=True)
    user_vote = IntegerField(read_only=True)
    contentTypeId = SerializerMethodField()

    # def get_user_vote(self, obj):
    #     request = self.context.get('request')
    #     if not request or not request.user.is_authenticated:
    #         print('not authenticated')
    #         return 0
    #     print('authenticated')
    #     from votes.models import Vote
    #     ct = ContentType.objects.get_for_model(type(obj), for_concrete_model=False)
    #     return (
    #         Vote.objects
    #         .filter(voter_id=request.user.id, content_type=ct, object_id=obj.pk)
    #         .values_list('value', flat=True)
    #         .first() or 0
    #     )

    def get_contentTypeId(self, obj):
        return ContentType.objects.get_for_model(type(obj), for_concrete_model=False).id

    class Meta:
        model=Comment
        fields="__all__"

    def validate_parent_comment(self, value):
        post_id = self.initial_data.get("post")
        if value and post_id and value.post_id != int(post_id):
            raise ValidationError("Parent comment must belong to the same post.")
        return value