from rest_framework.serializers import ModelSerializer, IntegerField
from ..models import Post

class PostSerializer(ModelSerializer):
    score = IntegerField(read_only=True)

    class Meta:
        model=Post
        fields="__all__"