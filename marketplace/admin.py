from django.contrib import admin
from .models import Profile, Property, Enquiry, ViewingRequest, SavedProperty, RealtorApplication

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "city", "is_verified", "created_at")
    list_filter = ("role", "is_verified", "city")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "phone")

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "city", "purpose", "price", "review_status", "owner_authorized", "created_at")
    list_filter = ("review_status", "purpose", "property_type", "state")
    search_fields = ("title", "city", "state", "owner__username")
    list_editable = ("review_status",)
    readonly_fields = ("slug", "created_at", "updated_at")

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("property", "name", "email", "phone", "created_at")
    search_fields = ("property__title", "name", "email", "phone")
    readonly_fields = ("created_at",)

@admin.register(ViewingRequest)
class ViewingRequestAdmin(admin.ModelAdmin):
    list_display = ("property", "name", "email", "preferred_date", "status")
    list_filter = ("status", "preferred_date")
    search_fields = ("property__title", "name", "email")

@admin.register(SavedProperty)
class SavedPropertyAdmin(admin.ModelAdmin):
    list_display = ("user", "property", "created_at")

@admin.register(RealtorApplication)
class RealtorApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "years_experience", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email", "licence_or_company")
    list_editable = ("status",)
