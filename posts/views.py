from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post
from .serializers.common import PostSerializer
from rest_framework.exceptions import NotFound, PermissionDenied
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
    
class PostDetailView(APIView):

    def get_post(self, pk):
        try:
            post = Post.objects.get(pk=pk)
            return post
        except Post.DoesNotExist as e:
            print(e)
            raise NotFound('Post not found.')

    def get(self, request, pk):
        post = self.get_post(pk)
        serialized_post = PostSerializer(post)
        return Response(serialized_post.data)
    
    def put(self, request, pk):
        post = self.get_post(pk)
        if post.poster != request.user:
            raise PermissionDenied('You do not have permission to update this post.')
        serialized_post = PostSerializer(post, data=request.data, partial=True)
        serialized_post.is_valid(raise_exception=True)
        serialized_post.save()
        return Response('HIT UPDATE ROUTE')
    
    def delete(self, request, pk):
        post = self.get_post(pk)
        if post.poster != request.user:
            raise PermissionDenied('You do not have permission to delete this post.')
        post.delete()
        return Response(status=204)
    