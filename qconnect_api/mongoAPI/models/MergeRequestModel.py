from djongo import models

class MergeRequest(models.Model):
    repositoryId = models.CharField(max_length=100)
    merge_request_id = models.IntegerField()
    data = models.JSONField()  # Stores the entire merge request data as JSON

    class Meta:
        indexes = [
            models.Index(fields=['repositoryId'], name='repo_id_index'),
            models.Index(fields=['merge_request_id'], name='merge_req_id_index'),
        ]
