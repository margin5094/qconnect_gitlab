from django.urls import path
from mongoAPI.controllers.tokenView import TokenAPIView
from mongoAPI.controllers.getRepoView import GitLabProjectsView
from mongoAPI.controllers.addRepositoryView import RepositoryAPIView
from mongoAPI.controllers.MergeRequestView import PRActiveNew, PRAvgTimeClose
from mongoAPI.controllers.ContributorsView import ActiveSumContributorsView
urlpatterns = [
    path('token/', TokenAPIView.as_view(), name='token_api'),
    path('gitlab/projects/', GitLabProjectsView.as_view(), name='gitlab-projects'),
    path('repository/', RepositoryAPIView.as_view(), name='add_repository'),
    path('active-new/', PRActiveNew.as_view(), name='pr_stats'),
    path('avg-time-close/',  PRAvgTimeClose.as_view(), name='avg_stats'),
    path('active-sum/', ActiveSumContributorsView.as_view(), name='active-contributors'),
]
