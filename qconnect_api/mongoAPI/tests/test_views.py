import unittest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory
from mongoAPI.controllers.tokenView import TokenAPIView
from mongoAPI.controllers.MergeRequestView import PRActiveNew, PRAvgTimeClose
from mongoAPI.controllers.ContributorsView import ActiveSumContributorsView, ActiveContributorsView, TopActiveContributorsView
from mongoAPI.controllers.getProjectsView import ReposForUserView
from mongoAPI.controllers.getRepoAddedView import GetAddedRepoView
from mongoAPI.controllers.synchronizeView import RefreshTokenActionAPIView
from mongoAPI.controllers.addRepositoryView import RepositoryAPIView
from mongoAPI.controllers.queue import send_task_to_queue,pika
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

#---------------------------SynchronizeView--------------------------
class TestRefreshTokenActionAPIView(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user_id = 'f4613ff9-8160-48f9-af20-5dc03c051e7f'

    @patch('mongoAPI.models.RepositoryModel.Repository.objects.get')
    @patch('mongoAPI.controllers.synchronizeView.send_task_to_queue')
    def test_refresh_token_action_success(self, mock_send_task_to_queue, mock_get):
        # Setup mock repository returned by the get call
        mock_repo = MagicMock()
        mock_repo.userId = self.user_id
        mock_repo.repoIds = {'repo1': 123, 'repo2': 456}
        mock_get.return_value = mock_repo

        # Mock send_task_to_queue as we don't want to actually send tasks during testing
        mock_send_task_to_queue.return_value = None

        # Make a post request to the view
        request = self.factory.post('/synchronize')
        response = RefreshTokenActionAPIView.as_view()(request)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), JsonResponse({
            'status': 'success',
            'message': 'Synchronization completed successfully.'
        }).content.decode())
        mock_send_task_to_queue.assert_called_once_with({
            'repository_ids': list(mock_repo.repoIds.keys()),
            'userId': self.user_id
        })

    @patch('mongoAPI.models.RepositoryModel.Repository.objects.get', side_effect=Repository.DoesNotExist)
    def test_refresh_token_action_repository_not_found(self, mock_get):
        # Make a post request to the view
        request = self.factory.post('/synchronize')
        response = RefreshTokenActionAPIView.as_view()(request)

        # Assertions for handling repository not found
        self.assertEqual(response.status_code, 404)
        self.assertIn('Repository not found', response.content.decode())

#---------------------------addRepository--------------------------
class TestRepositoryAPIView(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.url = '/repository'
        self.data = {
            'repositoryId': '123',
            'repositoryName': 'TestRepo'
        }

    @patch('mongoAPI.controllers.addRepositoryView.send_task_to_queue')
    @patch('mongoAPI.controllers.addRepositoryView.add_repository')
    def test_repository_api_view_success(self, mock_add_repository, mock_send_task_to_queue):
        # Setup the mocks to do nothing (success scenario)
        mock_add_repository.return_value = None
        mock_send_task_to_queue.return_value = None

        request = self.factory.post(self.url, data=self.data)
        response = RepositoryAPIView.as_view()(request)

        # Assertions for successful repository addition
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'repositoryId': 'Repository added successfully!'})
        mock_add_repository.assert_called_once_with('f4613ff9-8160-48f9-af20-5dc03c051e7f', 'TestRepo', '123')
        mock_send_task_to_queue.assert_called_once()

    def test_repository_api_view_missing_parameters(self):
        # Test missing parameters
        request = self.factory.post(self.url, data={'repositoryName': 'OnlyName'})
        response = RepositoryAPIView.as_view()(request)

        # Assertions for missing parameters
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Missing repositoryId or repositoryName'})

    @patch('mongoAPI.controllers.addRepositoryView.send_task_to_queue')
    @patch('mongoAPI.controllers.addRepositoryView.add_repository', side_effect=Exception("Test Exception"))
    def test_repository_api_view_exception(self, mock_add_repository, mock_send_task_to_queue):
        # Setup the mock for add_repository to raise an exception
        request = self.factory.post(self.url, data=self.data)
        response = RepositoryAPIView.as_view()(request)

        # Assertions for exception handling
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, {'error': 'Test Exception'})
        mock_add_repository.assert_called_once_with('f4613ff9-8160-48f9-af20-5dc03c051e7f', 'TestRepo', '123')
        mock_send_task_to_queue.assert_not_called()  # Assuming you don't send tasks if adding fails

class TestSendTaskToQueue(unittest.TestCase):
    @patch('mongoAPI.controllers.queue.pika.URLParameters')
    @patch('mongoAPI.controllers.queue.pika.BlockingConnection')
    @patch('mongoAPI.controllers.queue.os.getenv')
    def test_send_task_to_queue(self, mock_getenv, mock_BlockingConnection, mock_URLParameters):
        # Setup mocks
        mock_getenv.return_value = 'amqp://guest:guest@localhost'
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_BlockingConnection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel

        # Define the task data to be sent
        task_data = {"key": "value"}

        # Call the function under test
        send_task_to_queue(task_data)

        # Assertions to ensure the correct calls were made
        mock_getenv.assert_called_once_with('CLOUDAMQP_URL')
        mock_URLParameters.assert_called_once_with('amqp://guest:guest@localhost')
        mock_BlockingConnection.assert_called_once_with(mock_URLParameters.return_value)
        mock_connection.channel.assert_called_once()
        mock_channel.queue_declare.assert_called_once_with(queue='task_queue', durable=True)
        mock_channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key='task_queue',
            body=json.dumps(task_data),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        mock_connection.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()