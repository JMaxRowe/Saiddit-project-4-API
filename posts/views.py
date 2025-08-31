from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Post
from .serializers.common import PostSerializer
# Create your views here.

class PostListView(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serialized_posts = PostSerializer(posts, many=True)
        return Response(serialized_posts.data)