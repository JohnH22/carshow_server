from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


# Represents a vehicle in the system
# Matches the "CarEntry" data class fields from the Android application
class Vehicle(models.Model):
    # Vehicle Categories (Matches CarCategory Enum in Android)
    CATEGORY_CHOICES = [
        ('SEDAN', 'Sedan'), ('SUV', 'SUVs'), ('HATCHBACK', 'Hatchbacks'),
        ('STATION_WAGON', 'Station Wagons'), ('COUPE', 'Coupes'), ('CONVERTIBLE', 'Convertibles'),
        ('MOTORCYCLE', 'Motorcycles'), ('SCOOTER', 'Scooters & Minibikes'), ('TRUCK_4X4', 'Trucks & 4x4s'),
        ('VANS', 'Vans'), ('RV_CAMPER', 'RVs & Campers'), ('ELECTRIC_CAR', 'Electric Cars'),
        ('SUPERCAR', 'Supercars'), ('LUXURY', 'Luxury Cars'), ('CITY_CAR', 'City Cars'),
        ('HEAVY_TRUCK', 'Heavy Trucks'), ('CLASSIC_CAR', 'Classic Cars'), ('RIGHT_HAND_DRIVE', 'Right Hand Drive Cars'),
        ('SERVICE_VEHICLE', 'Service Vehicles'), ('HOT_ROD', 'Hot Rods'), ('CROSSOVER', 'Crossovers'),
        ('MUSCLE_CAR', 'Muscle Cars'), ('OFF_ROAD', 'Off-Roaders'), ('HYBRID_CAR', 'Hybrid Cars'),
        ('MINIVAN', 'Minivans'), ('BOAT', 'Boats'), ('UNKNOWN', 'Unknown')
    ]

    # Seller Types (Matches SellerType Enum in Android)
    SELLER_CHOICES = [
        ('PRIVATE', 'Private'),
        ('DEALER', 'Dealer'),
        ('UNKNOWN', 'Unknown')
    ]

# --- User ----
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')

# --- Core Vehicle Specifications ---
    brand = models.CharField(max_length=50, default="N/A")
    model_name = models.CharField(max_length=50) # Matches "model" in Android
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='UNKNOWN')
    year = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2) # Double in Android
    price_negotiable = models.BooleanField(default=False)
    image_url = models.URLField(max_length=500) # URL loaded as Bitmap via Glide/Coil in Android
    description = models.TextField(default="No description provided.")

# --- Technical Specifications ---
    engine = models.CharField(max_length=50, default='N/A')
    horsepower = models.IntegerField(default=0)
    drivetrain = models.CharField(max_length=10, default="FWD")
    transmission = models.CharField(max_length=20, default="Manual")
    torque = models.IntegerField(default=0)
    consumption = models.CharField(max_length=30, default="0.0 l/100km")
    mileage = models.IntegerField(default=0)

# --- Appearance & Dimensions ---
    interior_color = models.CharField(max_length=30, default="Black")
    exterior_color = models.CharField(max_length=30, default="White")
    wheel_size = models.IntegerField(default=17)
    doors = models.IntegerField(default=4)
    passengers = models.IntegerField(default=5)
    is_right_hand_drive = models.BooleanField(default=False)

# --- Location & Seller Info ---
    location = models.CharField(max_length=100, default="Unknown")
    seller_type = models.CharField(max_length=15, choices=SELLER_CHOICES, default='PRIVATE')

# --- Video URL ---
    video_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.year})"



# Represents a vehicle review/rating submitted by a user
# Matches the fields from "ReviewRequest" in the Android application
class Review(models.Model):
    # Relationship: One-To-Many (A vehicle can have multiple reviews)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='reviews')

    # --- User ---
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')

    comment = models.TextField()

    # Rating field bounded between 1.0 and 5.0 (Float in Django, Double in Android)
    rating = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review ({self.rating}/5) for {self.vehicle.model_name}"