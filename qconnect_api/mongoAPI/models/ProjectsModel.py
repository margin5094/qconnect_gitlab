from djongo import models

class Project(models.Model):
    userId = models.CharField(max_length=100, unique=True, primary_key=True)
    repos = models.JSONField()  # This will store a dictionary
    
    def __str__(self):
        return self.userId
