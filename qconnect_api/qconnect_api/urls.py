from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('aapi/', include('gitlabapi.urls')),
    path('api/', include('mongoAPI.urls')), 
]
