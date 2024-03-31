from djongo import models

class MergeRequest(models.Model):
    repositoryId = models.CharField(max_length=100)
    merge_request_id = models.IntegerField()
    state = models.CharField(max_length=50)  # New field for merge request state
    created_at = models.DateTimeField()  # New field for creation date
    merged_at= models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['repositoryId'], name='repo_id_index'),
            models.Index(fields=['merge_request_id'], name='merge_req_id_index'),
        ]
