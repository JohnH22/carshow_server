from django.contrib.auth.models import User
from django.db.models import Avg
from rest_framework import serializers
from vehicles.models import Vehicle, Review, VehicleImage


class UserSerializer(serializers.ModelSerializer):
    # Serializer for the Django User model
    # Shows which vehicles and reviews belong to user
    # Manages user registration
    vehicles = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    reviews = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'vehicles', 'reviews')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


# Serializer for the VehicleImage model
# Converts multiple image entries into nested JSON objects
class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ['image_url']


# Serializer for the Review model
# Converts Review instances into JSON and the opposite
class ReviewSerializer(serializers.ModelSerializer):
    # CharField allows us to display the actual username string in the JSON (like ReadOnlyField)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        # We include all fields: id, vehicle (ID), comment, rating, created_at
        fields = ['id', 'vehicle', 'rating', 'comment', 'created_at', 'username']

    def create(self, validated_data):
        # Automatically assign the request user as the author of the review
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user

        return super().create(validated_data)



# Serializer for the Vehicle model
# Includes nested reviews to provide full details to the Android app
class VehicleSerializer(serializers.ModelSerializer):
    # Fetches all images associated with the vehicle using the related_name="images"
    images = VehicleImageSerializer(many=True, required=False)
    # This fetches all reviews associated with the vehicle using the related_name="reviews"
    # many=True means a vehicle can have multiple reviews
    # read_only=True means we don't look for reviews data when creating a vehicle
    # (reviews field can be empty and server will ignore it)
    reviews = ReviewSerializer(many=True, read_only=True)
    # Displays the username of the person who posted the car (like ReadOnlyField)
    owner = serializers.CharField(source='owner.username', read_only=True)

    average_rating = serializers.SerializerMethodField()


    class Meta:
        model = Vehicle
        # Listing all fields to ensure exact mapping with Android's CarEntry
        fields = [
            'id', 'owner','brand', 'model_name', 'category', 'year', 'price',
            'price_negotiable', 'images', 'description', 'engine',
            'fuel_type', 'horsepower', 'drivetrain', 'transmission', 'torque',
            'consumption', 'mileage', 'interior_color', 'exterior_color',
            'wheel_size', 'doors', 'passengers', 'is_right_hand_drive',
            'location', 'seller_type', 'video_url', 'reviews', 'average_rating'
        ]

    # Dynamically calculates the average rating from the related 'Review' objects
    def get_average_rating(self, obj):
        if hasattr(obj, 'average_rating'):
            return round(obj.average_rating, 1)

        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0.0


    # Assign the currently authenticated user as the vehicle owner
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])

        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user

        vehicle = Vehicle.objects.create(**validated_data)


        # Process and save associated images
        for image_data in images_data:
            VehicleImage.objects.create(vehicle=vehicle, **image_data)

        return vehicle

