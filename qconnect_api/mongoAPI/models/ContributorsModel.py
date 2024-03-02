from djongo import models

class RepositoryContributors(models.Model):
    repositoryId = models.CharField(max_length=255, primary_key=True)
    totalContributors = models.IntegerField()

    def __str__(self):
        return f"{self.repositoryId} - {self.totalContributors}"
