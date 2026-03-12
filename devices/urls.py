from django.urls import path
from . import views

urlpatterns = [
    path('activate/', views.activate),
    path('', views.list_devices),
    path('<int:pk>/', views.device_detail),
]
