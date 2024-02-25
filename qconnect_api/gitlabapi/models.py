from django.db import models

class Repository(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    # Add more fields as needed
