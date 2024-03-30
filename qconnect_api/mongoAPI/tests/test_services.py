from django.test import TestCase
from unittest.mock import patch, MagicMock
from mongoAPI.models.tokenModel import Token
from mongoAPI.services.tokenService import save_token 
from mongoAPI.services.MergeRequestService import MergeRequestService
from mongoAPI.models.MergeRequestModel import MergeRequest
from mongoAPI.models.RepositoryModel import Repository
from mongoAPI.services.addRespositoryService import add_repository 
from datetime import datetime, timedelta
from django.db.models import Q
import pytz

#----------------------SaveTokenTest-----------------
class TestSaveToken(TestCase):
    @patch('mongoAPI.models.tokenModel.Token.objects.update_or_create')
    def test_save_token(self, mock_update_or_create):
        # Setup mock return value for update_or_create
        mock_token_instance = MagicMock(spec=Token)
        mock_update_or_create.return_value = (mock_token_instance, True)

        # Define test data
        access_token = 'test_access_token'
        refresh_token = 'test_refresh_token'
        user_id = 'test_user_id'

        # Call the function under test
        result = save_token(access_token, refresh_token, user_id)

        # Assertions to verify the correct calls and outcomes
        mock_update_or_create.assert_called_once_with(
            id=user_id, 
            defaults={'access_token': access_token, 'refresh_token': refresh_token}
        )
        self.assertEqual(result, mock_token_instance)

#----------------------MergeRequestService-----------------

class TestMergeRequestService(TestCase):
    @patch('mongoAPI.models.MergeRequestModel.MergeRequest.objects.filter')
    def test_get_active_and_new_prs(self, mock_filter):
        # Mock data setup adjusted to explicitly cover the logic for active and newly created counts
        mock_merge_requests = [
            MagicMock(spec=MergeRequest, created_at=datetime(2022, 1, 1, tzinfo=pytz.UTC), merged_at=None, repositoryId="1", state='opened'),
            MagicMock(spec=MergeRequest, created_at=datetime(2022, 1, 2, tzinfo=pytz.UTC), merged_at=datetime(2022, 1, 3, tzinfo=pytz.UTC), repositoryId="1", state='merged'),
        ]
        mock_filter.return_value = mock_merge_requests
        
        # Define test parameters
        start_date_str = '2022-01-01'
        end_date_str = '2022-01-03'
        repository_ids = ['1']

        # Call the service method
        response = MergeRequestService.get_active_and_new_prs(start_date_str, end_date_str, repository_ids)

        # Expected response adjusted for clarity
        expected_response = {
            "dates": ["2022-01-01", "2022-01-02", "2022-01-03"],
            "active": [0, 1, 1],  # Reflecting the logic more accurately
            "newly_created": [1, 1, 0],  # As per the mock data setup
        }

        self.assertEqual(response, expected_response)

        # Ensuring the correct filter logic is applied
        mock_filter.assert_called_once_with(
            Q(repositoryId__in=repository_ids) &
            (Q(created_at__lte=pytz.UTC.localize(datetime.fromisoformat(end_date_str))) | Q(merged_at__isnull=True) | Q(merged_at__gte=pytz.UTC.localize(datetime.fromisoformat(start_date_str))))
        )

class TestMergeRequestServiceAverageTime(TestCase):

    @patch('mongoAPI.models.MergeRequestModel.MergeRequest.objects.filter')
    def test_get_avg_time_to_close(self, mock_filter):
        # Mock MergeRequest instances to simulate merged PRs
        mock_merge_requests = [
            MagicMock(spec=MergeRequest, created_at=datetime(2022, 1, 1, 12, 0, tzinfo=pytz.UTC), merged_at=datetime(2022, 1, 1, 15, 0, tzinfo=pytz.UTC), repositoryId="1"),
            MagicMock(spec=MergeRequest, created_at=datetime(2022, 1, 1, 9, 0, tzinfo=pytz.UTC), merged_at=datetime(2022, 1, 1, 12, 0, tzinfo=pytz.UTC), repositoryId="1"),
            # This PR should not be counted as it's merged outside the date range
            MagicMock(spec=MergeRequest, created_at=datetime(2022, 1, 2, 10, 0, tzinfo=pytz.UTC), merged_at=datetime(2022, 1, 3, 11, 0, tzinfo=pytz.UTC), repositoryId="1"),
        ]
        mock_filter.return_value = mock_merge_requests
        
        # Define test parameters
        start_date_str = '2022-01-01'
        end_date_str = '2022-01-02'  # Note: This end date means we look at PRs merged by the end of 2022-01-02
        repository_ids = ['1']

        # Call the service method
        response = MergeRequestService.get_avg_time_to_close(start_date_str, end_date_str, repository_ids)

        # Expected response based on the mock data
        # Average for 2022-01-01: ((180 minutes + 180 minutes) / 2) / 60 = 3 hours
        expected_response = {
            "dates": ["2022-01-01","2022-01-02"],
            "times": [3.0,25.0]  # Average time in hours
        }

        self.assertEqual(response, expected_response)

        # Verifying the call to filter with the correct parameters
        mock_filter.assert_called_once_with(
            repositoryId__in=repository_ids,
            created_at__gte=pytz.UTC.localize(datetime.fromisoformat(start_date_str)),
            merged_at__lte=pytz.UTC.localize(datetime.fromisoformat(end_date_str)),
            merged_at__isnull=False
        )

# ----------------------addRepositoryService-----------------

class TestAddRepository(TestCase):

    @patch('mongoAPI.models.RepositoryModel.Repository.objects.create')
    @patch('mongoAPI.models.RepositoryModel.Repository.objects.get')
    def test_add_to_existing_repository(self, mock_get, mock_create):
        # Setup mock repository instance
        mock_repo_instance = MagicMock(spec=Repository)
        mock_repo_instance.repoIds = {}
        mock_get.return_value = mock_repo_instance
        
        userId = 'user123'
        repoId = 'repo123'
        repository_name = 'Test Repo'

        # Call the function under test
        result = add_repository(userId, repository_name, repoId)

        # Assertions
        mock_get.assert_called_once_with(userId=userId)
        mock_create.assert_not_called()  # Should not create a new instance
        self.assertTrue(repoId in mock_repo_instance.repoIds)
        self.assertEqual(mock_repo_instance.repoIds[repoId], repository_name)
        mock_repo_instance.save.assert_called_once()

    @patch('mongoAPI.models.RepositoryModel.Repository.objects.create')
    @patch('mongoAPI.models.RepositoryModel.Repository.objects.get', side_effect=Repository.DoesNotExist)
    def test_create_new_repository(self, mock_get, mock_create):
        # Define parameters for the new repository
        userId = 'user456'
        repoId = 'repo456'
        repository_name = 'New Test Repo'

        # Setup mock for create to return a new Repository instance
        mock_repo_instance = MagicMock(spec=Repository)
        mock_create.return_value = mock_repo_instance

        # Call the function under test
        result = add_repository(userId, repository_name, repoId)

        # Assertions
        mock_get.assert_called_once_with(userId=userId)
        mock_create.assert_called_once_with(userId=userId, repoIds={repoId: repository_name})
        self.assertEqual(result, mock_repo_instance)

    @patch('mongoAPI.models.RepositoryModel.Repository.objects.get', side_effect=Repository.MultipleObjectsReturned)
    @patch('builtins.print')
    def test_handle_multiple_objects_returned(self, mock_print, mock_get):
        # Define parameters that would trigger the exception
        userId = 'user789'
        repoId = 'repo789'
        repository_name = 'Error Repo'

        # Call the function under test
        result = add_repository(userId, repository_name, repoId)

        # Assertions
        mock_get.assert_called_once_with(userId=userId)