from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import RegistrationForm, PropertyForm, EnquiryForm, RealtorApplicationForm
from .models import Profile, Property, Enquiry, SavedProperty, RealtorApplication

def home(request):
    listings = Property.objects.filter(review_status=Property.Review.APPROVED)[:6]
    return render(request, "marketplace/home.html", {"listings": listings, "listing_count": Property.objects.filter(review_status=Property.Review.APPROVED).count()})

def property_list(request):
    listings = Property.objects.filter(review_status=Property.Review.APPROVED)
    q = request.GET.get("q", "").strip()
    city = request.GET.get("city", "").strip()
    kind = request.GET.get("type", "").strip()
    purpose = request.GET.get("purpose", "").strip()
    if q:
        listings = listings.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(city__icontains=q) | Q(state__icontains=q))
    if city:
        listings = listings.filter(Q(city__icontains=city) | Q(state__icontains=city))
    if kind:
        listings = listings.filter(property_type=kind)
    if purpose:
        listings = listings.filter(purpose=purpose)
    return render(request, "marketplace/properties.html", {"listings": listings, "q": q, "city": city, "kind": kind, "purpose": purpose,
        "types": Property.Type.choices, "purposes": Property.Purpose.choices})

def property_detail(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    if prop.review_status != Property.Review.APPROVED and not (request.user.is_authenticated and (request.user == prop.owner or request.user.is_staff)):
        from django.http import Http404
        raise Http404("Property not found")
    form = EnquiryForm()
    is_saved = request.user.is_authenticated and SavedProperty.objects.filter(user=request.user, property=prop).exists()
    return render(request, "marketplace/property_detail.html", {"property": prop, "enquiry_form": form, "is_saved": is_saved})

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.email = form.cleaned_data["email"]
        user.is_active = True
        user.save()
        Profile.objects.create(user=user, role=form.cleaned_data["role"], phone=form.cleaned_data.get("phone", ""), city=form.cleaned_data.get("city", ""))
        login(request, user)
        messages.success(request, "Your account is ready. Welcome to Urbisora Africa.")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    Profile.objects.get_or_create(user=request.user)
    mine = Property.objects.filter(owner=request.user)
    incoming = Enquiry.objects.filter(property__owner=request.user).select_related("property")[:10]
    saved = SavedProperty.objects.filter(user=request.user).select_related("property")[:8]
    applications = RealtorApplication.objects.filter(user=request.user)
    return render(request, "marketplace/dashboard.html", {"mine": mine, "incoming": incoming, "saved": saved, "applications": applications})

@login_required
def property_create(request):
    form = PropertyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        prop = form.save(commit=False)
        prop.owner = request.user
        prop.review_status = Property.Review.PENDING
        prop.save()
        messages.success(request, "Your listing has been submitted for review. It will appear publicly after approval.")
        return redirect("dashboard")
    return render(request, "marketplace/property_form.html", {"form": form})

@require_POST
def send_enquiry(request, slug):
    prop = get_object_or_404(Property, slug=slug, review_status=Property.Review.APPROVED)
    form = EnquiryForm(request.POST)
    if form.is_valid():
        enquiry = form.save(commit=False)
        enquiry.property = prop
        enquiry.sender = request.user if request.user.is_authenticated else None
        enquiry.save()
        messages.success(request, "Your enquiry has been recorded. The property owner can follow up using the contact details you provided.")
    else:
        messages.error(request, "Please check the enquiry form and try again.")
    return redirect("property_detail", slug=prop.slug)

@login_required
@require_POST
def toggle_saved(request, slug):
    prop = get_object_or_404(Property, slug=slug, review_status=Property.Review.APPROVED)
    item, created = SavedProperty.objects.get_or_create(user=request.user, property=prop)
    if not created:
        item.delete()
        messages.info(request, "Property removed from your saved list.")
    else:
        messages.success(request, "Property saved to your list.")
    return redirect("property_detail", slug=slug)

def realtor_directory(request):
    profiles = Profile.objects.filter(role=Profile.Role.REALTOR).filter(
        Q(is_verified=True) | Q(user__realtor_applications__status=RealtorApplication.Status.APPROVED)
    ).select_related("user").distinct().order_by("-is_verified", "user__first_name")
    return render(request, "marketplace/realtors.html", {"profiles": profiles})

@login_required
def realtor_apply(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = RealtorApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        app = form.save(commit=False)
        app.user = request.user
        app.save()
        profile.role = Profile.Role.REALTOR
        profile.years_experience = app.years_experience
        profile.save()
        messages.success(request, "Your realtor application has been submitted for review.")
        return redirect("dashboard")
    return render(request, "marketplace/realtor_apply.html", {"form": form})
