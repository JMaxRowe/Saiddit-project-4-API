from django.db import models
from users.models import User
from posts.models import Post
from django.contrib.contenttypes.fields import GenericRelation

class Comment(models.Model):
    is_deleted = models.BooleanField(default=False)

    body = models.TextField(max_length=750)
    created_at = models.DateTimeField(auto_now_add=True)
    commenter = models.ForeignKey(
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent_comment = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="replies"
    )

    votes = GenericRelation("votes.Vote", related_query_name="post")

    def soft_deleted(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    def __str__(self):
        return f"Comment by {self.commenter} on {self.post}"