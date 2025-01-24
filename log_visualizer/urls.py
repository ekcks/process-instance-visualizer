"""
URL configuration for log_visualizer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from log_viewer import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.index, name='index'),
    path('process_log/', views.process_log, name='process_log'),
    path('get_log_length/', views.get_log_length, name='get_log_length'),
    path('get_session_data/', views.get_session_data, name='get_log_length'),
    path('get_animation/', views.get_animation, name='get_animation'),
    path('process_group/', views.process_group, name='process_group'),
    path("__reload__/", include("django_browser_reload.urls")),
]
