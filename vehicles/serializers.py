from django.contrib.auth.models import User
from rest_framework import serializers
from vehicles.models import Vehicle, Review, VehicleImage


class UserSerializer(serializers.ModelSerializer):
    # Serializer for the Django User model
    # Shows which vehicles and reviews belong to user
    vehicles = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    reviews = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'vehicles', 'reviews')


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
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        # We include all fields: id, vehicle (ID), comment, rating, created_at
        fields = '__all__'



# Serializer for the Vehicle model
# Includes nested reviews to provide full details to the Android app
class VehicleSerializer(serializers.ModelSerializer):
    # Fetches all images associated with the vehicle using the related_name="images"
    images = VehicleImageSerializer(many=True, read_only=True)
    # This fetches all reviews associated with the vehicle using the related_name="reviews"
    # many=True means a vehicle can have multiple reviews
    # read_only=True means we don't look for reviews data when creating a vehicle
    # (reviews field can be empty and server will ignore it)
    reviews = ReviewSerializer(many=True, read_only=True)
    # Displays the username of the person who posted the car (like ReadOnlyField)
    owner = serializers.CharField(source='owner.username', read_only=True)


    class Meta:
        model = Vehicle
        # Listing all fields to ensure exact mapping with Android's CarEntry
        fields = [
            'id', 'owner','brand', 'model_name', 'category', 'year', 'price',
            'price_negotiable', 'images', 'description', 'engine',
            'fuel_type', 'drivetrain', 'transmission', 'torque',
            'consumption', 'mileage', 'interior_color', 'exterior_color',
            'wheel_size', 'doors', 'passengers', 'is_right_hand_drive',
            'location', 'seller_type', 'video_url', 'reviews'
        ]