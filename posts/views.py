from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post
from .serializers.common import PostSerializer
# Create your views here.

class PostListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        posts = Post.objects.all()
        serialized_posts = PostSerializer(posts, many=True)
        return Response(serialized_posts.data)
    
    def post(self, request):
        serialized_posts = PostSerializer(data=request.data)
        serialized_posts.is_valid(raise_exception=True)
        serialized_posts.save(poster=request.user)
        return Response(serialized_posts.data, 201)