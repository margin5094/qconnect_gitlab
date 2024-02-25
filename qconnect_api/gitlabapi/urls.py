from django.urls import path
from .views import RepositoryInfoAPIView

urlpatterns = [
    path('repository-info/', RepositoryInfoAPIView.as_view(), name='repository-info'),
]
