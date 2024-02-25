from djongo import models

class Repository(models.Model):
    # Define your MongoDB model fields here
    name = models.CharField(max_length=100)
    # Add other fields as needed
