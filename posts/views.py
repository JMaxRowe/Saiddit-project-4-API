from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Post
from votes.models import Vote
from .serializers.common import PostSerializer
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Sum, Count, Subquery, OuterRef, IntegerField, Value
from django.db.models.functions import Coalesce
from django.contrib.contenttypes.models import ContentType
# Create your views here.

class PostListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        user = request.user
        posts = Post.objects.select_related("poster", "community").annotate(
            score=Coalesce(Sum('votes__value'), 0),
            comments_count=Count("comments", distinct=True),
        )
        if user.is_authenticated:
            posts = posts.annotate(
                user_vote=Subquery(
                    Vote.objects.filter(
                        voter_id=user.id,
                        content_type=ContentType.objects.get_for_model(Post),
                        object_id=OuterRef("pk"),
                    ).values("value")[:1],
                    output_field=IntegerField()
                )
            )
        else:
            posts = posts.annotate(
                user_vote=Value(None, output_field=IntegerField())
            )
        serialized_posts = PostSerializer(posts, many=True)
        return Response(serialized_posts.data)
    
    def post(self, request):
        user = request.user
        serialized_posts = PostSerializer(data=request.data)
        serialized_posts.is_valid(raise_exception=True)
        created = serialized_posts.save(poster=request.user)
        post = Post.objects.select_related("poster", "community").filter(pk=created.pk).annotate(
            score = Coalesce(Sum('votes__value'), 0),
            comments_count=Count("comments", distinct=True),
        )
        if user.is_authenticated:
            post = post.annotate(
                user_vote=Subquery(
                    Vote.objects.filter(
                        voter_id=user.id,
                        content_type=ContentType.objects.get_for_model(Post),
                        object_id=OuterRef("pk"),
                    ).values("value")[:1],
                    output_field=IntegerField()
                )
            )
        else:
            post = post.annotate(
                user_vote=Value(None, output_field=IntegerField())
            )
        post = post.first()
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
        user = request.user
        post = Post.objects.select_related("poster", "community").filter(pk=pk).annotate(
            score=Coalesce(Sum("votes__value"), 0),
            comments_count=Count("comments", distinct=True),
        )
        if user.is_authenticated:
            post = post.annotate(
                user_vote=Subquery(
                    Vote.objects.filter(
                        voter_id=user.id,
                        content_type=ContentType.objects.get_for_model(Post),
                        object_id=OuterRef("pk"),
                    ).values("value")[:1],
                    output_field=IntegerField()
                )
            )
        else:
            post = post.annotate(
                user_vote=Value(None, output_field=IntegerField())
            )
        if not post:
            raise NotFound('Post not found.')
        post = post.first()
        serialized_post = PostSerializer(post)
        return Response(serialized_post.data)
    
    def put(self, request, pk):
        user = request.user
        post = self.get_post(pk)
        if post.poster != request.user:
            raise PermissionDenied('You do not have permission to update this post.')
        serialized_post = PostSerializer(post, data=request.data, partial=True)
        serialized_post.is_valid(raise_exception=True)
        serialized_post.save()
        updated_post = Post.objects.select_related("poster", "community").filter(pk=post.pk).annotate(
            score = Coalesce(Sum('votes__value'), 0),
            comments_count=Count("comments", distinct=True),
            
        ).first()
        if user.is_authenticated:
            post = post.annotate(
                user_vote=Subquery(
                    Vote.objects.filter(
                        voter_id=user.id,
                        content_type=ContentType.objects.get_for_model(Post),
                        object_id=OuterRef("pk"),
                    ).values("value")[:1],
                    output_field=IntegerField()
                )
            )
        else:
            post = post.annotate(
                user_vote=Value(None, output_field=IntegerField())
            )
        if not post:
            raise NotFound('Post not found.')
        post = post.first()
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