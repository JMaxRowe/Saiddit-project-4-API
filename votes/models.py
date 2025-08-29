from django.db import models
from users.models import User
from posts.models import Post
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Vote (models.Model):
    UPVOTE = 1
    DOWNVOTE = -1
    VOTE_CHOICES = [
        (UPVOTE, "Upvote"),
        (DOWNVOTE, "Downvote"),
    ]
    value = models.SmallIntegerField(choices=VOTE_CHOICES)
    voter = models.ForeignKey(
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='votes'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ("voter", "content_type", "object_id")
        
    def __str__(self):
        return f'{self.voter} voted {self.value} on {self.content_object}'