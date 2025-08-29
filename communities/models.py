from django.db import models
from users.models import User
# Create your models here.

class Community(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.CharField(max_length=250)
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_communities'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    members = models.ManyToManyField(
        User,
        through="CommunityMembership",
        related_name="communities"
    )

    def __str__(self):
        return self.name
    

class CommunityMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "community")

    def __str__(self):
        return f"{self.user.username} in {self.community.name}"
