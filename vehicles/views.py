from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters
from vehicles.models import Vehicle, Review
from vehicles.permissions import IsOwnerOrReadOnly
from vehicles.serializers import VehicleSerializer, ReviewSerializer, UserSerializer
from django.contrib.auth.models import User


class UserList(generics.ListAPIView):
    # Handles GET requests to list all users in the system
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    # Handles GET requests to fetch details of a specific user by ID
    queryset = User.objects.all()
    serializer_class = UserSerializer


# --- VEHICLE VIEWS ---
class VehicleList(generics.ListCreateAPIView):
    # Handles GET (List all vehicles with filtering, search & ordering) and POST (Create a new vehicle)
    # Perfect for the main screen of the Android app
    # Auto assigns the logged-in user as the owner
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    # Anyone can view , but only logged-in users can post a vehicle
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Enable both Filtering, Text Search and Ordering/Sorting
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Exact match filters (e.g., /api/vehicles/?brand=BMW)
    filterset_fields = ['brand', 'category', 'year', 'location', 'owner']

    # Free text search fields (e.g., /api/vehicles/?search=Corolla)
    # The "=" symbol means we want an EXACT match for the brand if searched
    search_fields = ['=brand', 'model_name', 'description']

    # Fields that the user/Android app is allowed to sort by
    ordering_fields = ['price', 'year', 'brand', 'created_at']

    # Default ordering when no parameter is passed (e.g., newest first)
    ordering = ('-created_at',)

    def perform_create(self, serializer):
        # Overrides perform_create to inject the current request user as the owner
        serializer.save(owner=self.request.user)


class VehicleDetail(generics.RetrieveUpdateDestroyAPIView):
    # Handles GET (Retrieve a specific vehicle by ID) , PUT (Update),
    # DELETE (Remove a vehicle)
    # For the vehicle details screen in Android
    # Ensures only the owner can modify it
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    # Anyone can view, but only the owner can PUT/PATCH/DELETE
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]



# --- REVIEW VIEWS ---
class ReviewList(generics.ListCreateAPIView):
    # Handles GET (List all reviews) and POST (Create a new review)
    # Auto assigns the logged-in user as the author
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # Only logged-in users can write a review
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Overrides perform_create to inject the current request user as the review author
        serializer.save(user=self.request.user)


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    # Handles GET, PUT, DELETE for a single review
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # Only the author can edit or delete their review
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]