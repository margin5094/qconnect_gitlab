from django.urls import path
from mongoAPI.controllers.tokenView import TokenAPIView
from mongoAPI.controllers.synchronizeView import RefreshTokenActionAPIView
from mongoAPI.controllers.addRepositoryView import RepositoryAPIView
from mongoAPI.controllers.MergeRequestView import PRActiveNew, PRAvgTimeClose
from mongoAPI.controllers.ContributorsView import ActiveSumContributorsView, ActiveContributorsView, TopActiveContributorsView
from mongoAPI.controllers.getProjectsView import ReposForUserView
urlpatterns = [
    path('token', TokenAPIView.as_view(), name='token_api'),
    path('synchronize', RefreshTokenActionAPIView.as_view(), name='synchronize_api'),
    path('projects', ReposForUserView.as_view(), name='repos-for-user'),
    path('repository', RepositoryAPIView.as_view(), name='add_repository'),
    path('active-new', PRActiveNew.as_view(), name='pr_stats'),
    path('avg-time-close',  PRAvgTimeClose.as_view(), name='avg_stats'),
    path('active-sum', ActiveSumContributorsView.as_view(), name='active-contributors'),
    path('active', ActiveContributorsView.as_view(), name='contributors-data'),
    path('most-active', TopActiveContributorsView.as_view(), name='top-active-contributors'),
]
