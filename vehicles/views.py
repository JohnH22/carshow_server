from django.db.models import Avg
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters
from vehicles.models import Vehicle, Review, VehicleImage
from vehicles.permissions import IsOwnerOrReadOnly
from vehicles.serializers import VehicleSerializer, ReviewSerializer, UserSerializer
from django.contrib.auth.models import User


# --- USER VIEWS ---
class UserList(generics.ListAPIView):
    # Handles GET requests to list all users in the system
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    # Handles GET requests to fetch details of a specific user by ID
    queryset = User.objects.all()
    serializer_class = UserSerializer



class UserRegister(generics.CreateAPIView):
    # Allows new user registration without requiring an existing login
    # Handles POST requests to register a new user
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # Anyone can register, no authentication required
    permission_classes = [permissions.AllowAny]




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
    # Mapping fields for advanced filtering (e.g., ?price__gte=1000)
    filterset_fields = {
        'brand': ['exact', 'icontains', 'iexact'],
        'model_name': ['exact', 'icontains', 'iexact'],
        'category': ['exact', 'icontains', 'iexact'],
        'seller_type': ['exact', 'icontains', 'iexact'],
        'location': ['exact', 'icontains', 'iexact'],
        'fuel_type': ['exact', 'icontains', 'iexact'],
        'owner': ['exact'],
        'transmission': ['exact', 'icontains', 'iexact'],
        'drivetrain': ['exact', 'icontains', 'iexact'],
        'exterior_color': ['exact', 'icontains', 'iexact'],
        'interior_color': ['exact', 'icontains', 'iexact'],

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
    ordering_fields = ['price', 'year', 'mileage', 'horsepower', 'engine', 'id', 'brand', 'model_name', 'consumption', 'average_rating']

    # Default ordering when no parameter is passed (e.g., newest first)
    ordering = ('-id',)


    # Annotate with average rating for sorting and display
    def get_queryset(self):
        return Vehicle.objects.annotate(
            average_rating=Coalesce(Avg('reviews__rating'), 0.0)
        )


    # Custom creation logic to handle nested image URLs
    def perform_create(self, serializer):
        # --- DEBUG START ---
        if not serializer.is_valid():
            print("DEBUG ERROR (POST):", serializer.errors)
        # --- DEBUG END ---

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



    # Custom update logic to refresh vehicle images efficiently
    def perform_update(self, serializer):
        # --- DEBUG START ---
        if not serializer.is_valid():
            print("DEBUG ERROR (PUT):", serializer.errors)
        # --- DEBUG END ---

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

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vehicle']

    def get_queryset(self):
        queryset = Review.objects.all()
        vehicle_id = self.request.GET.get('vehicle', None)
        if vehicle_id is not None:
            queryset = queryset.filter(vehicle_id=vehicle_id)
        return queryset

    def perform_create(self, serializer):
        # Overrides perform_create to inject the current request user as the review author
        serializer.save(user=self.request.user)


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    # Handles GET, PUT, DELETE for a single review
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # Only the author can edit or delete their review
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


