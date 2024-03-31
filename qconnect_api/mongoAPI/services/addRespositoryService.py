from mongoAPI.models.RepositoryModel import Repository

def add_repository(userId, repository_name, repoId):
    try:
        # Retrieve an existing repository by userId
        repository = Repository.objects.get(userId=userId)
        
        # Ensure repoIds is initialized and properly formatted
        repoIds = repository.repoIds if repository.repoIds else {}
        
        # Update the repository_name for the repoId; this will overwrite any existing entry for the repoId
        repoIds[repoId] = repository_name
        
        # Update the repoIds field and save the repository
        repository.repoIds = repoIds
        repository.save()

    except Repository.DoesNotExist:
        # If no existing repository matches the userId, create a new one
        # Initialize with repoId as the key and repository_name as its value
        repository = Repository.objects.create(
            userId=userId, 
            repoIds={repoId: repository_name}
        )

    except Repository.MultipleObjectsReturned:
        # Handle the unexpected case of multiple repositories with the same userId
        print("Error: Multiple repositories found for the given userId. UserId should be unique.")
        return None

    return repository
