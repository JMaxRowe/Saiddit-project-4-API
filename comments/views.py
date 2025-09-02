from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Comment
from votes.models import Vote
from .serializers.common import CommentSerializer
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Sum, OuterRef, Subquery, IntegerField, Value
from django.db.models.functions import Coalesce
from django.contrib.contenttypes.models import ContentType


class CommentListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        user = request.user
        comments = Comment.objects.select_related("commenter", "post").annotate(
            score=Coalesce(Sum("votes__value"), 0),
        )
        if user.is_authenticated:
            comments = comments.annotate(
                user_vote=Subquery(
                    Vote.objects.filter(
                        voter_id=user.id,
                        content_type=ContentType.objects.get_for_model(Comment),
                        object_id=OuterRef("pk"),
                    ).values("value")[:1],
                    output_field=IntegerField()
        )
    )
        else:
            comments = comments.annotate(
                user_vote=Value(None, output_field=IntegerField())
            )
        post_id = request.query_params.get("post")
        parent_id = request.query_params.get("parent")
        if post_id:
            comments = comments.filter(post_id=post_id)
        if parent_id is not None:
            if parent_id in ('', 'null', 'None'):
                comments = comments.filter(parent_comment__isnull=True)
            else:
                comments = comments.filter(parent_comment_id=parent_id)
        serialized_comments = CommentSerializer(comments, many=True)
        return Response(serialized_comments.data)

    def post(self, request):
        user = request.user
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created = serializer.save(commenter=request.user)
        comment = Comment.objects.select_related("commenter", "post").filter(pk=created.pk).annotate(
            score=Coalesce(Sum("votes__value"), 0),
        )
        if user.is_authenticated:
            comments = comments.annotate(
                user_vote=Subquery(
                    Vote.objects.filter(
                        voter_id=user.id,
                        content_type=ContentType.objects.get_for_model(Comment),
                        object_id=OuterRef("pk"),
                    ).values("value")[:1],
                    output_field=IntegerField()
                )
            )
        else:
            comments = comments.annotate(
                user_vote=Value(None, output_field=IntegerField())
            )
            comment = comment.first()
        return Response(CommentSerializer(comment).data, status=201)
    
class CommentDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_comment(self,request, pk):
        try:
            user = request.user
            comment = Comment.objects.select_related("commenter", "post").annotate(
                score=Coalesce(Sum("votes__value"), 0),
                
            ).get(pk=pk)
            if user.is_authenticated:
                comment = comment.annotate(
                    user_vote=Subquery(
                        Vote.objects.filter(
                            voter_id=user.id,
                            content_type=ContentType.objects.get_for_model(Comment),
                            object_id=OuterRef("pk"),
                        ).values("value")[:1],
                        output_field=IntegerField()
                    )
                )
            else:
                comment = comment.annotate(
                    user_vote=Value(None, output_field=IntegerField())
                )
                return comment
        except Comment.DoesNotExist:
            raise NotFound("Comment not found.")
        
    def get(self, request, pk):
        user = request.user
        comment = self.get_comment(pk)
        serialized_comment = CommentSerializer(comment)
        replies = comment.replies.select_related("commenter", "post").annotate(
            score=Coalesce(Sum("votes__value"), 0),
        )

        serialized_replies = CommentSerializer(replies, many=True)
        return Response({
            'comment': serialized_comment.data,
            'replies': serialized_replies.data
        })

    def put(self, request, pk):
        user = request.user
        comment = self.get_comment(pk)
        if comment.commenter != request.user:
            raise PermissionDenied('You do not have permission to update this comment.')
        serialized_comment = CommentSerializer(comment, data=request.data, partial=True)
        serialized_comment.is_valid(raise_exception=True)
        serialized_comment.save()
        updated = Comment.objects.filter(pk=comment.pk).annotate(
            score=Coalesce(Sum("votes__value"), 0),
        ).first()
        if user.is_authenticated:
            comment = comment.annotate(
                user_vote=Subquery(
                    Vote.objects.filter(
                        voter_id=user.id,
                        content_type=ContentType.objects.get_for_model(Comment),
                        object_id=OuterRef("pk"),
                    ).values("value")[:1],
                    output_field=IntegerField()
                )
            )
        else:
            comment = comment.annotate(
                user_vote=Value(None, output_field=IntegerField())
            )
            comment = comment.first()
        return Response(CommentSerializer(updated).data)
    
    def delete(self, request, pk):
        comment = self.get_comment(pk)
        if comment.commenter != request.user:
            raise PermissionDenied('You do not have permission to delete this comment.')
        comment.delete()
        return Response({'status': 'deleted'}, status=204)
    
class CommentRestoreView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist as e:
            print(e)
            raise NotFound('comment not found.')
        if comment.commenter != request.user:
            raise PermissionDenied('You do not have permission to restore this comment.')
        comment.restore()
        return Response({'status': 'restored'},status=200)