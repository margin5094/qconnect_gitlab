from djongo import models

class PaginationInfo(models.Model):
    repository_id = models.CharField(max_length=255, unique=True,primary_key=True)
    merge_requests_last_page = models.IntegerField(default=1)
    branches = models.JSONField(default=list)

    class Meta:
        db_table = 'repository_info'
