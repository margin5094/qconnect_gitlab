from djongo import models

class Project(models.Model):
    userId = models.CharField(max_length=100, unique=True, primary_key=True)
    # Assuming each repositoryName maps to multiple repoIds
    repos = models.JSONField()  # This will store a dictionary
    
    def __str__(self):
        return self.userId
