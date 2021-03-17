from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser
from django.contrib.auth.models import UserManager
from django.utils import timezone


class Author(AbstractBaseUser, PermissionsMixin):

    name = models.CharField(max_length=32)
    username = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=32)

    objects = UserManager()

    USERNAME_FIELD = "username"

    def __str__(self):
        return f"{self.id}: {self.username}"


class NewsStory(models.Model):

    available_categories = [("pol", "politics"), ("art", "art news"), ("tech", "technology"), ("trivia", "trivial news")]
    available_regions = [("uk", "United Kingdom news"), ("eu", "European news"), ("w", "World news")]

    headline = models.CharField(max_length=64)
    category = models.CharField(choices=available_categories, max_length=6)
    region = models.CharField(choices=available_regions, max_length=2)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    creation_date = models.DateField(default=timezone.now)
    details = models.CharField(max_length=512)

    def __str__(self):
        return f"{self.id}: {self.author.name}: {self.headline}"


