from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Property, Enquiry, RealtorApplication, ContactMessage

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
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account already uses this email address.")
        return email


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = (
            "photo", "professional_title", "agency_name", "phone", "show_phone",
            "show_email", "city", "bio", "specialties", "languages",
            "service_areas", "website", "linkedin_url", "years_experience",
        )
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 6, "placeholder": "Your experience, approach, market knowledge and what clients can expect."}),
            "specialties": forms.TextInput(attrs={"placeholder": "Residential sales, rentals, land, commercial"}),
            "languages": forms.TextInput(attrs={"placeholder": "English, Hausa, Yoruba…"}),
            "service_areas": forms.TextInput(attrs={"placeholder": "Guzape, Asokoro, Maitama, Abuja"}),
        }

    def __init__(self, *args, **kwargs):
        self.account_user = kwargs.pop("account_user", None)
        super().__init__(*args, **kwargs)
        if self.account_user:
            self.fields["first_name"].initial = self.account_user.first_name
            self.fields["last_name"].initial = self.account_user.last_name
            self.fields["email"].initial = self.account_user.email
        self.fields["photo"].required = False

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.account_user:
            qs = qs.exclude(pk=self.account_user.pk)
        if qs.exists():
            raise forms.ValidationError("That email address is already in use.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = self.account_user or profile.user
        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data["last_name"].strip()
        user.email = self.cleaned_data["email"].strip().lower()
        if commit:
            user.save()
            profile.save()
        return profile


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = (
            "title", "description", "property_type", "purpose", "price", "city", "state",
            "address", "bedrooms", "bathrooms", "area_sqm", "image_url", "owner_authorized",
        )
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


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("full_name", "email", "phone", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 5, "placeholder": "How can our team help?"})}
