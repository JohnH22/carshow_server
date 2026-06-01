from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters
from vehicles.models import Vehicle, Review, VehicleImage
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

    # ADVANCED FILTERING (Using a Dictionary instead of a List)
    filterset_fields = {
        'brand': ['exact'],
        'category': ['exact'],
        'seller_type': ['exact'],
        'location': ['exact'],
        'owner': ['exact'],
        'transmission': ['exact'],
        'drivetrain': ['exact'],
        'exterior_color': ['exact'],
        'interior_color': ['exact'],

        # Boolean Filters (True/False)
        'price_negotiable': ['exact'],
        'is_right_hand_drive': ['exact'],

        # Enables Range Filtering for Price, Year, Mileage, Horsepower, Torque
        'price': ['exact', 'gte', 'lte'],
        'year': ['exact', 'gte', 'lte'],
        'mileage': ['exact', 'gte', 'lte'],
        'horsepower': ['exact', 'gte', 'lte'],
        'torque': ['exact', 'gte', 'lte'],

        # Enables Range Filtering for Numeric Fields
        'engine': ['exact', 'gte', 'lte'],  # Allows: ?engine__gte=1400&engine__lte=2000
        'consumption': ['exact', 'gte', 'lte'],  # Allows: ?consumption__lte=6.5

        # Enables Range Filtering for Dimensions/Capacity
        'doors': ['exact', 'gte', 'lte'],
        'passengers': ['exact', 'gte', 'lte'],
        'wheel_size': ['exact', 'gte', 'lte'],
    }

    # Free text search fields (e.g., /api/vehicles/?search=Corolla)
    search_fields = ['brand', 'model_name', 'description', 'location']

    # Fields that the user/Android app is allowed to sort by
    ordering_fields = ['price', 'year', 'mileage', 'horsepower', 'engine', 'id']

    # Default ordering when no parameter is passed (e.g., newest first)
    ordering = ('-id',)

    def perform_create(self, serializer):
        # Save the vehicle and automatically assign the logged-in user as the owner
        vehicle = serializer.save(owner=self.request.user)


        # Get the images array sent by the Android app from the raw request data
        # Bypasses PyCharm's strict type warning since 'data' is injected dynamically by DRF
        # noinspection PyUnresolvedReferences
        images_data = self.request.data.get('images', [])

        # Process each image entry to populate the separate VehicleImage table
        for image_data in images_data:
            # Handle both scenarios: if Android sends a list of strings ["url1", "url2"]
            # or a list of objects [{"image_url": "url1"}]
            if isinstance(image_data, dict):
                url = image_data.get('image_url')
            else:
                url = image_data

                # If a valid URL exists, create a new row linked to this vehicle (One-to-Many)
                if url:
                    VehicleImage.objects.create(vehicle=vehicle, image_url=url)


class VehicleDetail(generics.RetrieveUpdateDestroyAPIView):
    # Handles GET (Retrieve a specific vehicle by ID) , PUT (Update),
    # DELETE (Remove a vehicle)
    # For the vehicle details screen in Android
    # Ensures only the owner can modify it
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    # Anyone can view, but only the owner can PUT/PATCH/DELETE
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        # Save the updated core vehicle fields (brand, model, price, etc.)
        vehicle = serializer.save()

        # Extract the new list of images from the raw request data
        # Bypasses PyCharm's strict type warning since 'data' is injected dynamically by DRF
        # noinspection PyUnresolvedReferences
        images_data = self.request.data.get('images', None)

        # If the 'images' key was provided in the update request, refresh the image set
        if images_data is not None:
            # Clear all previously linked images to prevent "orphan" records in the database
            vehicle.images.all().delete()

            # Loop through the new list to save the updated image URLs in the database
            for image_data in images_data:
                # Support both formats: a nested JSON object or a raw string URL
                url = image_data.get('image_url') if isinstance(image_data, dict) else image_data
                # If a valid URL exists, create a new row linked to this vehicle (One-to-Many)
                if url:
                    VehicleImage.objects.create(vehicle=vehicle, image_url=url)



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