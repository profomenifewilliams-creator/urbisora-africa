from django.conf import settings
from django.db import models
from django.utils.text import slugify

class Profile(models.Model):
    class Role(models.TextChoices):
        CLIENT = "client", "Client"
        REALTOR = "realtor", "Realtor"
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    phone = models.CharField(max_length=40, blank=True)
    city = models.CharField(max_length=80, blank=True)
    bio = models.TextField(blank=True)
    years_experience = models.PositiveSmallIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Property(models.Model):
    class Type(models.TextChoices):
        APARTMENT = "apartment", "Apartment"
        HOUSE = "house", "House"
        LAND = "land", "Land"
        COMMERCIAL = "commercial", "Commercial"
        SHORT_STAY = "short_stay", "Short stay"
    class Purpose(models.TextChoices):
        SALE = "sale", "For sale"
        RENT = "rent", "For rent"
        LEASE = "lease", "For lease"
    class Review(models.TextChoices):
        PENDING = "pending", "Pending review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="properties")
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=205, unique=True, blank=True)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=Type.choices, default=Type.APARTMENT)
    purpose = models.CharField(max_length=10, choices=Purpose.choices, default=Purpose.SALE)
    price = models.DecimalField(max_digits=16, decimal_places=2)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default="FCT")
    address = models.CharField(max_length=250, blank=True)
    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    area_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(blank=True, help_text="Optional publicly hosted property image URL")
    owner_authorized = models.BooleanField(default=False)
    review_status = models.CharField(max_length=12, choices=Review.choices, default=Review.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:180] or "property"
            candidate = base
            suffix = 2
            while Property.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{suffix}"
                suffix += 1
            self.slug = candidate
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title

class Enquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="enquiries")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"Enquiry for {self.property} by {self.name}"

class ViewingRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="viewing_requests")
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    preferred_date = models.DateField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

class SavedProperty(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "property"], name="unique_saved_property")]

class RealtorApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending review"
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="realtor_applications")
    message = models.TextField()
    years_experience = models.PositiveSmallIntegerField(default=0)
    licence_or_company = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
