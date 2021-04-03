from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
    name = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.item.name} IS OWNED BY {self.user.username}"
