from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Comment
from votes.models import Vote
from .serializers.common import CommentSerializer
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Sum, Count, Subquery, OuterRef, IntegerField, Value, Q
from django.db.models.functions import Coalesce
from django.contrib.contenttypes.models import ContentType



class CommentListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        user = request.user
        votes = Vote.objects.filter(
            content_type = ContentType.objects.get_for_model(Comment),
            object_id=OuterRef("pk"),
        ).values("object_id").annotate(score = Sum('value')).values('score')

        comments = (
            Comment.objects.select_related("commenter", "post")
            .annotate(
                score=Coalesce(Subquery(votes), 0),
                replies_count=Count("replies", distinct=True),
            )
        )
        print('out')
        if user.is_authenticated:
            print('in')
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
                user_vote=Value(0, output_field=IntegerField())
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

        votes = Vote.objects.filter(
            content_type = ContentType.objects.get_for_model(Comment),
            object_id=OuterRef("pk"),
        ).values("object_id").annotate(score = Sum('value')).values('score')

        comment = Comment.objects.select_related("commenter", "post").filter(pk=created.pk).annotate(
            score=Coalesce(Subquery(votes), 0),
            replies_count=Count("replies", distinct=True),
        ).first()
        return Response(CommentSerializer(comment, context={"request": request}).data, status=201)
    
class CommentDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_comment(self, pk):

        votes = Vote.objects.filter(
            content_type = ContentType.objects.get_for_model(Comment),
            object_id=OuterRef("pk"),
        ).values("object_id").annotate(score = Sum('value')).values('score')

        comment = Comment.objects.select_related("commenter", "post").filter(pk=pk).annotate(
            score=Coalesce(Subquery(votes), 0),
            replies_count=Count("replies", distinct=True),
        ).first()
        if not comment:
            raise NotFound("Comment not found.")
        return comment
        
    def get(self, request, pk):
        comment = self.get_comment(pk)
        serialized_comment = CommentSerializer(comment, context={"request": request})

        votes = Vote.objects.filter(
            content_type = ContentType.objects.get_for_model(Comment),
            object_id=OuterRef("pk"),
        ).values("object_id").annotate(score = Sum('value')).values('score')

        replies = comment.replies.all().select_related("commenter", "post").annotate(
            score=Coalesce(Subquery(votes), 0),
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
        serialized_comment = CommentSerializer(comment, context={'request': request})
        return Response(serialized_comment.data, status=200)
    
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
        serialized_comment = CommentSerializer(comment, context={'request': request})
        return Response(serialized_comment.data, status=200)