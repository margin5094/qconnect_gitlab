from djongo import models
from djongo.models import ObjectIdField

class Token(models.Model):
    id = models.CharField(max_length=100, unique=True, primary_key=True)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)

    def __str__(self):
        return self.id
