from rest_framework.serializers import ModelSerializer, ValidationError
from ..models import Vote
from django.contrib.contenttypes.models import ContentType

class VoteSerializer(ModelSerializer):
    class Meta:
        model=Vote
        fields="__all__"

    def validate(self, attrs):
        content: ContentType = attrs["content_type"]
        object_id = attrs["object_id"]
        if (content.app_label, content.model) not in {("posts", "post"), ("comments", "comment")}:
            raise ValidationError({"content_type": "Unsupported target type."})
        model = content.model_class()
        if not model.objects.filter(pk=object_id).exists():
            raise ValidationError({"object_id": "Target does not exist."})
        return attrs