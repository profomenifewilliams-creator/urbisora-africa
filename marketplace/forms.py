from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Property, Enquiry, RealtorApplication

User = get_user_model()

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    phone = forms.CharField(max_length=40, required=False)
    city = forms.CharField(max_length=80, required=False)
    role = forms.ChoiceField(choices=Profile.Role.choices)
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone", "city", "role", "password1", "password2")
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account already uses this email address.")
        return email

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ("title", "description", "property_type", "purpose", "price", "city", "state", "address",
                  "bedrooms", "bathrooms", "area_sqm", "image_url", "owner_authorized")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "owner_authorized": forms.CheckboxInput(),
        }
    def clean_owner_authorized(self):
        if not self.cleaned_data.get("owner_authorized"):
            raise forms.ValidationError("You must confirm you own this property or have the owner's written authorisation.")
        return True
    def clean_price(self):
        value = self.cleaned_data["price"]
        if value <= 0:
            raise forms.ValidationError("Enter a price greater than zero.")
        return value

class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ("name", "email", "phone", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}

class RealtorApplicationForm(forms.ModelForm):
    class Meta:
        model = RealtorApplication
        fields = ("message", "years_experience", "licence_or_company")
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}
