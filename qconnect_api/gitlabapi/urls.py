from django.urls import path
from .views import RepositoryInfoAPIView, AddRepositoryAPIView

urlpatterns = [
    path('repository-info/', RepositoryInfoAPIView.as_view(), name='repository-info'),
    path('add-repository/', AddRepositoryAPIView.as_view(), name='add-repository'),
]
