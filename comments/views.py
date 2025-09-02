from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Comment
from .serializers.common import CommentSerializer
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce


class CommentListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        comments = Comment.objects.select_related("commenter", "post").annotate(
            score=Coalesce(Sum("votes__value"), 0),
            replies_count=Count("replies", distinct=True),
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
        return Response(CommentSerializer(comments, many=True, context={"request": request}).data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        created = serializer.save(commenter=request.user)
        comment = Comment.objects.select_related("commenter", "post").filter(pk=created.pk).annotate(
            score=Coalesce(Sum("votes__value"), 0),
            replies_count=Count("replies", distinct=True),
        ).first()
        return Response(CommentSerializer(comment, context={"request": request}).data, status=201)
    
class CommentDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_comment(self, pk):
        comment = Comment.objects.select_related("commenter", "post").filter(pk=pk).annotate(
            score=Coalesce(Sum("votes__value"), 0),
            replies_count=Count("replies", distinct=True),
        ).first()
        if not comment:
            raise NotFound("Comment not found.")
        return comment
        
    def get(self, request, pk):
        comment = self.get_comment(pk)
        serialized_comment = CommentSerializer(comment, context={"request": request})
        replies = comment.replies.all().select_related("commenter", "post").annotate(
            score=Coalesce(Sum("votes__value"), 0),
            replies_count=Count("replies", distinct=True),
        )
        serialized_replies = CommentSerializer(replies, many=True, context={"request": request})
        return Response({
            'comment': serialized_comment.data,
            'replies': serialized_replies.data
        })

    def put(self, request, pk):
        comment = self.get_comment(pk)
        if comment.commenter != request.user:
            raise PermissionDenied('You do not have permission to update this comment.')
        serialized_comment = CommentSerializer(comment, data=request.data, partial=True, context={"request": request})
        serialized_comment.is_valid(raise_exception=True)
        serialized_comment.save()
        updated = self.get_comment(pk)
        return Response(CommentSerializer(updated, context={"request": request}).data)
    
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