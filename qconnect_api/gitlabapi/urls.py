from django.urls import path
from .views import RepositoryInfoAPIView, AddRepositoryAPIView, TopGitUsersAPIView,  ActiveContributorsCountAPIView, GitUsersActiveAPIView

urlpatterns = [
    path('repository-info/', RepositoryInfoAPIView.as_view(), name='repository-info'),
    path('add-repository/', AddRepositoryAPIView.as_view(), name='add-repository'),
    path('top-git-users/', TopGitUsersAPIView.as_view(), name='top-git-users'),
    path('git-users/active-sum', ActiveContributorsCountAPIView.as_view(), name='active-contributors-count'),
    path('git-users/active', GitUsersActiveAPIView.as_view(), name='git-users-active'),
]
