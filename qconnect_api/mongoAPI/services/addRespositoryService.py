from mongoAPI.models.RepositoryModel import Repository

def add_repository(repository_id, repository_name,userId):
    repository, created = Repository.objects.update_or_create(
        id=repository_id,
        defaults={'repositoryName': repository_name,'userId':userId}
    )
    return repository
