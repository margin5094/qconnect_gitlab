from django.test import TestCase
from mongoAPI.models.tokenModel import Token
from mongoAPI.models.RepositoryModel import Repository
from mongoAPI.models.ProjectsModel import Project
from mongoAPI.models.PaginationInfo import PaginationInfo
from mongoAPI.models.MergeRequestModel import MergeRequest
from mongoAPI.models.CommitsModel import Commit
from django.utils import timezone
from datetime import timedelta

# Test cases for the Token model
class TokenModelTest(TestCase):

    def test_create_token(self):
        """Test token creation without mocking."""
        Token.objects.create(id='test_user', access_token='access123', refresh_token='refresh123')
        token = Token.objects.get(id='test_user')
        self.assertEqual(token.access_token, 'access123')
        self.assertEqual(token.refresh_token, 'refresh123')

    def test_update_token(self):
        """Test token update without mocking."""
        Token.objects.create(id='test_user', access_token='old_access', refresh_token='old_refresh')
        token, created = Token.objects.update_or_create(id='test_user', defaults={'access_token': 'new_access', 'refresh_token': 'new_refresh'})
        self.assertFalse(created)  # False indicates that an existing record was updated
        self.assertEqual(token.access_token, 'new_access')
        self.assertEqual(token.refresh_token, 'new_refresh')

# Test cases for the Repository model
class RepositoryModelTest(TestCase):

    def setUp(self):
        # Set up data for the tests with the updated structure for repoIds
        self.test_user_id = 'user123'
        self.test_repo_ids = {
            '88011': 'CSCI5193_TI_ParkEasy',
            '88012': 'CSCI5194_EasyPark',
            '88013': 'CSCI5195_ParkNow'
        }
        Repository.objects.create(userId=self.test_user_id, repoIds=self.test_repo_ids)

    def test_repository_creation(self):
        """Test the creation of a Repository model instance with updated repoIds structure."""
        repository = Repository.objects.get(userId=self.test_user_id)
        self.assertEqual(repository.userId, self.test_user_id)
        self.assertDictEqual(repository.repoIds, self.test_repo_ids, "The repoIds structure does not match as expected")

    def test_repository_string_representation(self):
        """Test the string representation of a Repository model instance."""
        repository = Repository.objects.get(userId=self.test_user_id)
        self.assertEqual(str(repository), self.test_user_id, "The string representation of the Repository does not match the expected userId")

    def test_repository_update(self):
        """Test updating the Repository model instance with a new repoIds structure."""
        new_repo_ids = {
            '88014': 'CSCI5196_SmartPark',
            '88015': 'CSCI5197_ParkQuick'
        }
        Repository.objects.filter(userId=self.test_user_id).update(repoIds=new_repo_ids)
        repository_updated = Repository.objects.get(userId=self.test_user_id)
        self.assertDictEqual(repository_updated.repoIds, new_repo_ids, "The updated repoIds structure does not match as expected")

# Test cases for the Project model
class ProjectModelTest(TestCase):

    def setUp(self):
        # Set up data for the tests with the updated structure for repos
        self.test_user_id = 'user123_project'
        self.test_repos = {
            '64739': 'mmpatel',
            '64989': 'mmpatel',
            '65070': 'mmpatel',
            '67463': 'group26'
        }
        Project.objects.create(userId=self.test_user_id, repos=self.test_repos)

    def test_project_creation(self):
        """Test the creation of a Project model instance with updated repos structure."""
        project = Project.objects.get(userId=self.test_user_id)
        self.assertEqual(project.userId, self.test_user_id)
        self.assertDictEqual(project.repos, self.test_repos, "The repos structure does not match as expected")

    def test_project_string_representation(self):
        """Test the string representation of a Project model instance."""
        project = Project.objects.get(userId=self.test_user_id)
        self.assertEqual(str(project), self.test_user_id, "The string representation of the Project does not match the expected userId")

    def test_project_update(self):
        """Test updating the Project model instance with a new repos structure."""
        new_repos = {
            '67890': 'newrepo1',
            '67891': 'newrepo2'
        }
        Project.objects.filter(userId=self.test_user_id).update(repos=new_repos)
        project_updated = Project.objects.get(userId=self.test_user_id)
        self.assertDictEqual(project_updated.repos, new_repos, "The updated repos structure does not match as expected")

# Test cases for the Pagination model
class PaginationInfoModelTest(TestCase):

    def setUp(self):
        # Set up initial PaginationInfo instance for tests
        self.repository_id = '65f2725bf6215854d4ee3d24'
        self.initial_merge_requests_last_page = 1
        self.initial_branches = [
            {"name": "main", "last_commit_page": 10},
            {"name": "develop", "last_commit_page": 5}
        ]
        
        PaginationInfo.objects.create(
            repository_id=self.repository_id,
            merge_requests_last_page=self.initial_merge_requests_last_page,
            branches=self.initial_branches
        )

    def test_pagination_info_creation(self):
        """Test the creation of a PaginationInfo model instance."""
        pagination_info = PaginationInfo.objects.get(repository_id=self.repository_id)
        self.assertEqual(pagination_info.repository_id, self.repository_id)
        self.assertEqual(pagination_info.merge_requests_last_page, self.initial_merge_requests_last_page)
        self.assertListEqual(pagination_info.branches, self.initial_branches, "The branches JSON structure does not match")

    def test_pagination_info_update(self):
        """Test updating the PaginationInfo model instance."""
        updated_merge_requests_last_page = 5
        updated_branches = [
            {"name": "feature-1", "last_commit_page": 8},
            {"name": "hotfix-1", "last_commit_page": 4}
        ]
        PaginationInfo.objects.filter(repository_id=self.repository_id).update(
            merge_requests_last_page=updated_merge_requests_last_page,
            branches=updated_branches
        )
        
        pagination_info_updated = PaginationInfo.objects.get(repository_id=self.repository_id)
        self.assertEqual(pagination_info_updated.merge_requests_last_page, updated_merge_requests_last_page)
        self.assertListEqual(pagination_info_updated.branches, updated_branches, "The branches were not updated correctly")

    def test_pagination_info_string_representation(self):
        """Test the string representation of a PaginationInfo model instance."""
        pagination_info = PaginationInfo.objects.get(repository_id=self.repository_id)
        self.assertEqual(str(pagination_info), self.repository_id)

class MergeRequestModelTest(TestCase):

    def setUp(self):
        # Merge request instance for testing
        self.repositoryId = 'repo123'
        self.merge_request_id = 1
        self.state = 'open'
        self.created_at = timezone.now()
        self.merged_at = None  # Assuming it's not merged yet

        MergeRequest.objects.create(
            repositoryId=self.repositoryId,
            merge_request_id=self.merge_request_id,
            state=self.state,
            created_at=self.created_at,
            merged_at=self.merged_at
        )

    def test_merge_request_creation(self):

        merge_request = MergeRequest.objects.get(merge_request_id=self.merge_request_id)
        self.assertEqual(merge_request.repositoryId, self.repositoryId)
        self.assertEqual(merge_request.state, self.state)
        self.assertAlmostEqual(merge_request.created_at.timestamp(), self.created_at.timestamp(), delta=timedelta(seconds=1).total_seconds())
        self.assertEqual(merge_request.merged_at, self.merged_at)
    
    def test_merge_request_update(self):

        updated_state = 'merged'
        updated_merged_at = timezone.now()  # Assuming the merge request is now merged
        MergeRequest.objects.filter(merge_request_id=self.merge_request_id).update(
            state=updated_state,
            merged_at=updated_merged_at
        )
        updated_merge_request = MergeRequest.objects.get(merge_request_id=self.merge_request_id)
        self.assertEqual(updated_merge_request.state, updated_state)
        self.assertAlmostEqual(updated_merge_request.merged_at.timestamp(), updated_merged_at.timestamp(), delta=timedelta(seconds=1).total_seconds())
    
    def test_indexes_existence(self):
      
        indexes = MergeRequest._meta.indexes
        self.assertTrue(any(index.fields == ['repositoryId'] for index in indexes), "Index on 'repositoryId' not found")
        self.assertTrue(any(index.fields == ['merge_request_id'] for index in indexes), "Index on 'merge_request_id' not found")


class CommitModelTest(TestCase):

    def setUp(self):
        # Set up initial Commit instance for tests
        self.commit_id = 'abc123'
        self.repository_id = 'repo123'
        self.committer_name = 'John Doe'
        self.committer_email = 'john.doe@example.com'
        self.committed_date = timezone.now()
        
        Commit.objects.create(
            commitId=self.commit_id,
            repositoryId=self.repository_id,
            committer_name=self.committer_name,
            committer_email=self.committer_email,
            committed_date=self.committed_date
        )

    def test_commit_creation(self):
        """Verify a Commit instance can be successfully created and retrieved."""
        commit = Commit.objects.get(commitId=self.commit_id)
        self.assertEqual(commit.commitId, self.commit_id)
        self.assertEqual(commit.repositoryId, self.repository_id)
        self.assertEqual(commit.committer_name, self.committer_name)
        self.assertEqual(commit.committer_email, self.committer_email)
        self.assertAlmostEqual(commit.committed_date.timestamp(), self.committed_date.timestamp(), delta=1)

    def test_commit_string_representation(self):
        """Test the string representation of a Commit model instance."""
        commit = Commit.objects.get(commitId=self.commit_id)
        self.assertEqual(str(commit), self.commit_id)
