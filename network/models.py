from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    # default fields (username, email, password) are enough for this project
    pass

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(default=timezone.now)

    def likes_count(self):
        return self.likes.count()

    def __str__(self):
        return f"{self.author.username}: {self.content[:30]}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_set")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers_set")

    class Meta:
        unique_together = ("follower", "followed")

    def __str__(self):
        return f"{self.follower.username} -> {self.followed.username}"

class Comment(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey("User", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}: {self.content[:30]}"
