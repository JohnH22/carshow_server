from django.contrib import admin
from vehicles.models import Vehicle, Review, VehicleImage

# This allows managing multiple vehicle images directly inside the Vehicle edit page
class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1 # Number of empty URL slots to display by default


# Customizes the Vehicle presentation in the Django Admin panel
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model_name', 'year', 'price', 'owner')
    list_filter = ('category', 'seller_type', 'brand')
    search_fields = ('brand', 'model_name', 'location')
    # Embed the images layout inside the vehicle details page
    inlines = [VehicleImageInline]


# Customizes the Review presentation in the Django Admin panel
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'user__username', 'vehicle__model_name')