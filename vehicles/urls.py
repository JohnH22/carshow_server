from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from vehicles import views


urlpatterns = [
    # Endpoints for Django Users
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),

    # Endpoints for Vehicles
    path('vehicles/', views.VehicleList.as_view(), name='vehicle-list'),
    path('vehicles/<int:pk>/', views.VehicleDetail.as_view(), name='vehicle-detail'),

    # Endpoints for Reviews
    path('reviews/', views.ReviewList.as_view(), name='review-list'),
    path('reviews/<int:pk>/', views.ReviewDetail.as_view(), name='review-detail'),
]

# Allows the API to handle format suffixes like /vehicles/.json
urlpatterns = format_suffix_patterns(urlpatterns)