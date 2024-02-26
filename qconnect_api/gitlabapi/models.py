from djongo import models

class Repository(models.Model):
    # Define your MongoDB model fields here
    name = models.CharField(max_length=100)
    # Add other fields as needed

class Commit(models.Model):
    commit_id = models.CharField(max_length=50, unique=True)
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    committed_date = models.DateTimeField()

    def __str__(self):
        return self.commit_id