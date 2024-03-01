from djongo import models

class Repository(models.Model):
    # Here mongoDb object id is also objectId for repoId
    id = models.CharField(max_length=100, unique=True, primary_key=True) #this is repo_id
    repositoryName = models.CharField(max_length=200)
    userId= models.CharField(max_length=200) 
    def __str__(self):
        return self.id