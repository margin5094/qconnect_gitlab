import unittest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory
from mongoAPI.controllers.tokenView import TokenAPIView
from mongoAPI.controllers.MergeRequestView import PRActiveNew, PRAvgTimeClose
from mongoAPI.controllers.ContributorsView import ActiveSumContributorsView, ActiveContributorsView, TopActiveContributorsView
from mongoAPI.controllers.getProjectsView import ReposForUserView
from mongoAPI.controllers.getRepoAddedView import GetAddedRepoView
from mongoAPI.models.RepositoryModel import Repository
from mongoAPI.models.ProjectsModel import Project
from django.http import JsonResponse
from rest_framework import status
import json

#---------------------------TokenAPI---------------------------
class TestTokenAPIView(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('mongoAPI.controllers.tokenView.fetch_and_store_gitlab_projects')
    @patch('mongoAPI.controllers.tokenView.save_token')
    def test_valid_tokens(self, mock_save_token, mock_fetch_and_store):
        mock_save_token.return_value = None
        mock_fetch_and_store.return_value = {'status': 'success'}

        request = self.factory.post('/token', {'access_token': 'valid_access_token', 'refresh_token': 'valid_refresh_token'})
        response = TokenAPIView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'status': 'Token saved successfully'})
        mock_save_token.assert_called_once_with('valid_access_token', 'valid_refresh_token', 'f4613ff9-8160-48f9-af20-5dc03c051e7f')
        mock_fetch_and_store.assert_called_once_with('f4613ff9-8160-48f9-af20-5dc03c051e7f', 'valid_access_token')


    @patch('mongoAPI.controllers.tokenView.fetch_and_store_gitlab_projects')
    @patch('mongoAPI.controllers.tokenView.save_token')
    def test_invalid_tokens(self, mock_save_token, mock_fetch_and_store):
        mock_save_token.return_value = None
        mock_fetch_and_store.return_value = {'status': 'error', 'message': 'Invalid token'}

        request = self.factory.post('/token/', {})
        response = TokenAPIView.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'error': 'Invalid request'})
        mock_save_token.assert_not_called()
        mock_fetch_and_store.assert_not_called()


#---------------------------MergeRequest--------------------------
class TestPRActiveNew(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('mongoAPI.controllers.MergeRequestView.MergeRequestService.get_active_and_new_prs')
    def test_active_new(self, mock_merge_request_service):
        
        mock_merge_request_service.return_value= [
            {
                "dates": ["2024-03-15", "2024-03-16"],
                "active": [10, 15],
                "newly_created": [5, 8]
            }
        ]

        url = '/active-new?startDate=2024-03-15&endDate=2024-03-16&repositoryIds=1&repositoryIds=2'

        # Create POST request with data (if applicable)
        request = self.factory.post(url, data=None, format='json')

        # Invoke the view
        response = PRActiveNew.as_view()(request)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [{"dates": ["2024-03-15", "2024-03-16"], "active": [10, 15], "newly_created": [5, 8]}]
        )
        mock_merge_request_service.assert_called_once_with('2024-03-15', '2024-03-16', ['1', '2'])

class TestPRAvgTimeClose(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('mongoAPI.controllers.MergeRequestView.MergeRequestService.get_avg_time_to_close')
    def test_avg_time_close(self, mock_merge_request_service):
        mock_merge_request_service.return_value = {
            "dates": ["2024-03-15", "2024-03-16"],
            "times": [3, 4]
        }

        url = '/avg-time-close?startDate=2024-03-15&endDate=2024-03-16&repositoryIds=1&repositoryIds=2'

        # Create POST request with data (if applicable)
        request = self.factory.post(url, data=None, format='json')
        response = PRAvgTimeClose.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"dates": ["2024-03-15", "2024-03-16"], "times": [3, 4]})
        mock_merge_request_service.assert_called_once_with('2024-03-15', '2024-03-16', ['1', '2'])

#---------------------------Contributors--------------------------

class TestActiveSumContributorsView(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('mongoAPI.controllers.ContributorsView.get_unique_contributors_count')
    def test_active_sum_contributors(self, mock_contributors_count):
        mock_contributors_count.return_value = 5

        url = '/active-sum-contributors?startDate=2024-03-15&endDate=2024-03-16&repositoryIds=1&repositoryIds=2'

        # Create POST request with data (if applicable)
        request = self.factory.post(url, data=None, format='json')
        
        # Invoke the view
        response = ActiveSumContributorsView.as_view()(request)
        response_data = json.loads(response.content.decode('utf-8'))
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, {'count': 5})
        mock_contributors_count.assert_called_once_with('2024-03-15', '2024-03-16', ['1', '2'])

class TestActiveContributorsView(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('mongoAPI.controllers.ContributorsView.get_contributors_data')  # Adjust the import path
    def test_active_contributors(self, mock_get_contributors_data):
        # Adjust the mock return value to match the expected response structure
        mock_response = [
            {
                "dates": ["2024-03-15", "2024-03-16"],
                "activeUsers": [10, 20],
                "totalUsers": [100, 200]
            }
        ]
        mock_get_contributors_data.return_value = mock_response

        url = '/active-contributors?startDate=2024-03-15&endDate=2024-03-16&repositoryIds=1&repositoryIds=2'
        request = self.factory.post(url, data=None, format='json')
        response = ActiveContributorsView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        # Adjust the expected value in the assertion to match the mock response
        self.assertEqual(response.data, mock_response)
        mock_get_contributors_data.assert_called_once_with('2024-03-15', '2024-03-16', ['1', '2'])

class TestTopActiveContributorsView(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('mongoAPI.controllers.ContributorsView.get_top_active_contributors') 
    def test_top_active_contributors(self, mock_get_top_active_contributors):
        # Adjust the mock return value to match the expected response structure
        expected_response = [
            {
                "email": "mr353045@dal.ca",
                "commits": 55,
                "name": "Margin Mukeshbhai Patel"
            },
            {
                "email": "ns672795@dal.ca",
                "commits": 13,
                "name": "nisargs"
            },
        ]
        mock_get_top_active_contributors.return_value = expected_response

        url = '/top-active-contributors?startDate=2024-03-15&endDate=2024-03-16&repositoryIds=1&repositoryIds=2'
        request = self.factory.post(url, data=None, format='json')
        response = TopActiveContributorsView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_response)
        mock_get_top_active_contributors.assert_called_once_with('2024-03-15', '2024-03-16', ['1', '2'])

#---------------------------getProjects--------------------------
class TestReposForUserView(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('mongoAPI.models.ProjectsModel.Project.objects.get')
    def test_get_repos_for_user_success(self, mock_get):
        # Mock successful retrieval of a Project
        mock_project = Project()
        mock_project.userId = 'f4613ff9-8160-48f9-af20-5dc03c051e7f'
        mock_project.repos = {'repoNames': ['Repo1', 'Repo2']}
        mock_get.return_value = mock_project

        # Make request to the view
        request = self.factory.get('/projects')
        response = ReposForUserView.as_view()(request)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'repoNames': ['Repo1', 'Repo2']})

    @patch('mongoAPI.models.ProjectsModel.Project.objects.get')
    def test_get_repos_for_user_not_found(self, mock_get):
        # Mock Project.DoesNotExist exception
        mock_get.side_effect = Project.DoesNotExist

        # Make request to the view
        request = self.factory.get('/projects')
        response = ReposForUserView.as_view()(request)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Project not found for the provided userId."})

#---------------------------getRepoAddedbyUser--------------------------
class TestGetAddedRepoView(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('mongoAPI.models.RepositoryModel.Repository.objects.get')
    def test_get_added_repo_success(self, mock_get):
        # Mock successful retrieval of a Repository
        mock_repository = Repository()
        mock_repository.userId = 'f4613ff9-8160-48f9-af20-5dc03c051e7f'
        mock_repository.repoIds = {'repoIds': [123, 456]}
        mock_get.return_value = mock_repository

        # Make request to the view
        request = self.factory.get('/added-repos')
        response = GetAddedRepoView.as_view()(request)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), JsonResponse({
            'status': 'success',
            'repoIds': {'repoIds': [123, 456]}
        }).content.decode())

    @patch('mongoAPI.models.RepositoryModel.Repository.objects.get')
    def test_get_added_repo_not_found(self, mock_get):
        # Mock Repository.DoesNotExist exception
        mock_get.side_effect = Repository.DoesNotExist

        # Make request to the view
        request = self.factory.get('/added-repos')
        response = GetAddedRepoView.as_view()(request)

        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode(), JsonResponse({
            'status': 'error', 'message': 'Repository not found'
        }, status=404).content.decode())   


if __name__ == '__main__':
    unittest.main()