from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Post
from .serializers.common import PostSerializer
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
# Create your views here.

class PostListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        posts = Post.objects.select_related("poster", "community").annotate(
            score=Coalesce(Sum('votes__value'), 0),
            comments_count=Count("comments", distinct=True)
        )
        serialized_posts = PostSerializer(posts, many=True)
        return Response(serialized_posts.data)
    
    def post(self, request):
        serialized_posts = PostSerializer(data=request.data)
        serialized_posts.is_valid(raise_exception=True)
        created = serialized_posts.save(poster=request.user)
        post = Post.objects.select_related("poster", "community").filter(pk=created.pk).annotate(
            score = Coalesce(Sum('votes__value'), 0),
            comments_count=Count("comments", distinct=True)
        ).first()
        return Response(PostSerializer(post).data, 201)
    
class PostDetailView(APIView):

    def get_post(self, pk):
        try:
            post = Post.objects.get(pk=pk)
            return post
        except Post.DoesNotExist as e:
            print(e)
            raise NotFound('Post not found.')

    def get(self, request, pk):
        post = Post.objects.select_related("poster", "community").filter(pk=pk).annotate(
            score=Coalesce(Sum("votes__value"), 0),
            comments_count=Count("comments", distinct=True)
        ).first()
        if not post:
            raise NotFound('Post not found.')
        serialized_post = PostSerializer(post)
        return Response(serialized_post.data)
    
    def put(self, request, pk):
        post = self.get_post(pk)
        if post.poster != request.user:
            raise PermissionDenied('You do not have permission to update this post.')
        serialized_post = PostSerializer(post, data=request.data, partial=True)
        serialized_post.is_valid(raise_exception=True)
        serialized_post.save()
        updated_post = Post.objects.select_related("poster", "community").filter(pk=post.pk).annotate(
            score = Coalesce(Sum('votes__value'), 0),
            comments_count=Count("comments", distinct=True)
        ).first()
        reserialized_post = PostSerializer(updated_post)
        return Response(reserialized_post.data)
    
    def delete(self, request, pk):
        post = self.get_post(pk)
        if post.poster != request.user:
            raise PermissionDenied('You do not have permission to delete this post.')
        post.delete()
        return Response({'status': 'deleted'}, status=204)
    
class PostRestoreView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist as e:
            print(e)
            raise NotFound('Post not found.')
        if post.poster != request.user:
            raise PermissionDenied('You do not have permission to restore this post.')
        post.restore()
        return Response({'status': 'restored'},status=200)