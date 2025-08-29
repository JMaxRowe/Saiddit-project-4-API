from django.db import models
from users.models import User
from communities.models import Community


class Post(models.Model):
    POST_TYPES = [
        ("text", "Text"),
        ("image", "Image"),
        ("video", "Video"),
    ]
    title = models.CharField(max_length=75)
    body = models.TextField(max_length=1000)
    type = models.CharField(max_length=5, choices=POST_TYPES)
    poster = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title