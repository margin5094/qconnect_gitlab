from django.urls import path
from mongoAPI.controllers.tokenView import TokenAPIView
from mongoAPI.controllers.getRepoView import GitLabProjectsView
from mongoAPI.controllers.addRepositoryView import RepositoryAPIView

urlpatterns = [
    path('token/', TokenAPIView.as_view(), name='token_api'),
    path('gitlab/projects/', GitLabProjectsView.as_view(), name='gitlab-projects'),
    path('repository/', RepositoryAPIView.as_view(), name='add_repository'),
]
