from djongo import models

class Commit(models.Model):
    commitId = models.CharField(max_length=255, primary_key=True)
    repositoryId = models.CharField(max_length=255)
    committer_name = models.CharField(max_length=255, null=True)
    committer_email = models.EmailField(max_length=255, null=True)
    committed_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.commitId

    class Meta:
        indexes = [
            models.Index(fields=['commitId', 'repositoryId']),
        ]
        unique_together = [['commitId', 'repositoryId']]  # This ensures that the combination of commitId and repositoryId is unique
