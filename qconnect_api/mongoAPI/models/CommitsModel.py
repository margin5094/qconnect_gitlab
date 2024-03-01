from djongo import models

class Commit(models.Model):
    commitId = models.CharField(max_length=255, primary_key=True)
    data = models.JSONField()

    def __str__(self):
        return self.commitId
