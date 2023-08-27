# from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Ticket(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="ticket_images/", null=True, blank=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True)

    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.headline

class UserFollows(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following_users")
    followed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followed_by_users")
    followed_tickets = models.ManyToManyField(Ticket, related_name="followers")

    class Meta:
        unique_together = ("created_by", "followed_user")
