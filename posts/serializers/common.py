from rest_framework.serializers import ModelSerializer, IntegerField, CharField, URLField, ValidationError, SerializerMethodField
from ..models import Post
from users.serializers.common import OwnerSerializer
from communities.serializers.common import CommunitySerializer

class PostSerializer(ModelSerializer):
    body = CharField(required=False, allow_blank=True)
    media_url = URLField(required=False, allow_blank=True)

    score = IntegerField(read_only=True)
    comments_count = IntegerField(read_only=True)
    poster = OwnerSerializer(read_only=True)
    community = CommunitySerializer(read_only=True)
    user_vote = IntegerField(read_only=True)


    class Meta:
        model=Post
        fields="__all__"

    def validate(self, attrs):
        post_type = attrs.get("type") or getattr(self.instance, "type", None)
        body = attrs.get("body", getattr(self.instance, "body", ""))
        media_url = attrs.get("media_url", getattr(self.instance, "media_url", ""))
        errors = {}

        if post_type == "text":
            if not body:
                errors["body"] = ["Body is required for text posts"]
            if media_url:
                errors["media_url"] = ["media_url must be empty for text posts."]
        elif post_type in ("image", "video"):
            if not media_url:
                errors["media_url"] = [f"media_url is required for {post_type} posts."]
            if body is None:
                attrs["body"] = ""
        else:
            errors["type"] = ["invalid or missing post type."]
        if errors:
            raise ValidationError(errors)
        return attrs