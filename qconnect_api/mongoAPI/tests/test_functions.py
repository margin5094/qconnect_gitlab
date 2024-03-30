from unittest.mock import patch, MagicMock, call
from django.test import TestCase
from mongoAPI.services.functionService import fetch_and_store_gitlab_projects  # Adjust the import path
from mongoAPI.Constants import GITLAB_API_URL
from mongoAPI.services.functionService import fetch_and_store_merge_requests  # Adjust import path
from mongoAPI.models.MergeRequestModel import MergeRequest
from mongoAPI.models.PaginationInfo import PaginationInfo
from mongoAPI.services.functionService import update_branches_info,get_gitlab_branches,fetch_and_store_commits,fetch_commits_for_branch
from mongoAPI.models.CommitsModel import Commit
from django.utils.dateparse import parse_datetime

# ----------------------FetchGitlabProjects-----------------
class TestGitlabProjects(TestCase):

    @patch('mongoAPI.services.functionService.requests.get')
    @patch('mongoAPI.models.ProjectsModel.Project.objects.update_or_create')
    def test_fetch_and_store_gitlab_projects(self, mock_update_or_create, mock_get):
        # Setup mock response for requests.get
        mock_response = MagicMock()
        mock_response.json.return_value = [{'id': 1, 'name': 'Project 1'}]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Assume update_or_create always creates a new object for simplicity
        mock_update_or_create.return_value = (MagicMock(), True)

        userId = 'user123'
        access_token = 'token123'

        response = fetch_and_store_gitlab_projects(userId, access_token)

        # Verify that requests.get was called correctly
        mock_get.assert_called_once()
        # This checks the URL and headers; adjust as needed
        args, kwargs = mock_get.call_args
        self.assertTrue(GITLAB_API_URL in args[0])
        self.assertEqual(kwargs['headers']['Authorization'], f'Bearer {access_token}')

        # Verify that update_or_create was called correctly
        mock_update_or_create.assert_called_once_with(
            userId=userId, defaults={'repos': {'1': 'Project 1'}}
        )

        # Verify response
        self.assertEqual(response, {"status": "success", "message": "Projects fetched and stored successfully.", "created": True})

# ----------------------Fetch And Store Merge Request-----------------
class TestFetchAndStoreMergeRequestsDetailed(TestCase):
    @patch('mongoAPI.services.functionService.requests.get')
    @patch('mongoAPI.models.MergeRequestModel.MergeRequest.objects.bulk_create')
    @patch('mongoAPI.models.MergeRequestModel.MergeRequest.objects.filter')
    @patch('mongoAPI.models.PaginationInfo.PaginationInfo.objects.update_or_create')
    def test_fetch_and_store_merge_requests_detailed(self, mock_update_or_create, mock_filter, mock_bulk_create, mock_get):
        # Setup mock for GitLab API response
        mock_response = MagicMock()
        mock_response.json.side_effect = [
            [{'id': 1, 'created_at': '2022-01-01T00:00:00Z', 'merged_at': '2022-01-02T00:00:00Z', 'state': 'merged'}],
            []  # Second call returns an empty list, simulating end of pagination
        ]
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Mock PaginationInfo update_or_create
        mock_pagination_info_instance = MagicMock(spec=PaginationInfo)
        mock_pagination_info_instance.merge_requests_last_page = 1
        mock_update_or_create.return_value = (mock_pagination_info_instance, True)

        # Mock MergeRequest filter to simulate no existing merge requests
        mock_filter.return_value = MagicMock(values_list=MagicMock(return_value=[]))

        # Define test parameters
        repositoryId = '123'
        access_token = 'fake_token'
        base_url = f"{GITLAB_API_URL}projects/{repositoryId}/merge_requests"
        headers = {'Authorization': f'Bearer {access_token}'}
        # Call the function under test
        fetch_and_store_merge_requests(repositoryId, access_token)

        # Assertions to verify the correct call arguments for bulk_create
        mock_bulk_create.assert_called_once()
        bulk_create_call_args = mock_bulk_create.call_args[0][0]  # Extracting the list passed to bulk_create
        self.assertIsInstance(bulk_create_call_args, list)
        self.assertEqual(len(bulk_create_call_args), 1)  # Assert one merge request was processed
        self.assertIsInstance(bulk_create_call_args[0], MergeRequest)
        self.assertEqual(bulk_create_call_args[0].merge_request_id, 1)
        self.assertEqual(bulk_create_call_args[0].state, 'merged')

        # Verify the pagination info was updated correctly
        self.assertEqual(mock_pagination_info_instance.merge_requests_last_page, 1)  # Assert it's incremented correctly
        mock_pagination_info_instance.save.assert_called_once()

        # Further assertions can verify the call arguments to requests.get to ensure correct pagination handling
        expected_calls = [
            call(base_url, headers=headers, params={'per_page': 100, 'page': 1}),
            call(base_url, headers=headers, params={'per_page': 100, 'page': 2})  # Assuming pagination incremented
        ]
        self.assertEqual(mock_get.call_args_list, expected_calls)

# ----------------------Fetch Commits -----------------
class UpdateBranchesInfoTest(TestCase):

    @patch('mongoAPI.services.functionService.get_gitlab_branches')
    @patch('mongoAPI.models.PaginationInfo.PaginationInfo.objects.get_or_create')
    def test_update_branches_info(self, mock_get_or_create, mock_get_gitlab_branches):
        mock_get_gitlab_branches.return_value = [{'name': 'master'}, {'name': 'dev'}]
        mock_repo_info = MagicMock(spec=PaginationInfo)
        mock_repo_info.branches = [{'name': 'master', 'last_commit_page': 1}]
        mock_get_or_create.return_value = (mock_repo_info, True)

        update_branches_info('repository_id', 'access_token')

        # Verify branches are updated correctly
        expected_branches = [{'name': 'master', 'last_commit_page': 1}, {'name': 'dev', 'last_commit_page': 1}]
        self.assertEqual(mock_repo_info.branches, expected_branches)

class GetGitlabBranchesTest(TestCase):
    @patch('mongoAPI.services.functionService.requests.get')
    def test_get_gitlab_branches(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'name': 'master'}, {'name': 'dev'}]
        mock_get.return_value = mock_response

        branches = get_gitlab_branches('repository_id', 'access_token')

        self.assertEqual(len(branches), 2)
        self.assertIn({'name': 'master'}, branches)

class FetchAndStoreCommitsTest(TestCase):
    @patch('mongoAPI.services.functionService.fetch_commits_for_branch')
    @patch('mongoAPI.models.PaginationInfo.PaginationInfo.objects.get')
    @patch('mongoAPI.models.CommitsModel.Commit.objects.filter')
    @patch('mongoAPI.models.CommitsModel.Commit.objects.bulk_create')
    def test_fetch_and_store_commits_without_executor(self, mock_bulk_create, mock_filter, mock_get, mock_fetch_commits_for_branch):
        # Setup mock responses
        mock_repo_info = MagicMock()
        mock_repo_info.branches = [{'name': 'master', 'last_commit_page': 1}]
        mock_get.return_value = mock_repo_info

        # Mock the branch fetching function to return mock commits
        mock_fetch_commits_for_branch.return_value = (
            [{
                'id': 'commit1',
                'committed_date': '2022-01-01T00:00:00Z',
                'committer_name': 'Alice',
                'committer_email': 'alice@example.com'
            }],
            2
        )

        mock_filter.return_value = MagicMock(values_list=MagicMock(return_value=[]))

        # Call the function under test
        fetch_and_store_commits('repository_id', 'access_token')

        # Extract the list of Commit instances passed to bulk_create
        commits_created = mock_bulk_create.call_args[0][0]

        # Assert that the correct number of commits were passed to bulk_create
        self.assertEqual(len(commits_created), 1)

        # Detailed attribute verification for each commit
        commit = commits_created[0]
        self.assertEqual(commit.commitId, 'commit1')
        self.assertEqual(commit.repositoryId, 'repository_id')
        self.assertEqual(commit.committer_name, 'Alice')
        self.assertEqual(commit.committer_email, 'alice@example.com')
        self.assertEqual(commit.committed_date, parse_datetime('2022-01-01T00:00:00Z'))

        # Ensure ignore_conflicts is passed correctly to bulk_create
        _, kwargs = mock_bulk_create.call_args
        self.assertTrue(kwargs.get('ignore_conflicts', False))