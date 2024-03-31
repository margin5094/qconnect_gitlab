from djongo import models

class Repository(models.Model):
    userId = models.CharField(max_length=100, unique=True, primary_key=True)

    repoIds = models.JSONField()  # This will store a dictionary
    
    def __str__(self):
        return self.userId
