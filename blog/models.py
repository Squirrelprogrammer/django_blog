from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title: str = models.CharField(max_length=200)
    text: str = models.TextField()
    created_date: datetime = models.DateTimeField(default=timezone.now)
    published_date: datetime = models.DateTimeField(blank=True, null=True)

    def publish(self) -> None:
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title
