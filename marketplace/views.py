from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    RegistrationForm, PropertyForm, EnquiryForm, RealtorApplicationForm,
    ProfileForm, ContactMessageForm,
)
from .models import Profile, Property, Enquiry, SavedProperty, RealtorApplication


def home(request):
    listings = Property.objects.filter(
        review_status=Property.Review.APPROVED, is_archived=False
    ).select_related("owner", "owner__profile")[:6]
    return render(request, "marketplace/home.html", {
        "listings": listings,
        "listing_count": Property.objects.filter(review_status=Property.Review.APPROVED, is_archived=False).count(),
    })


def property_list(request):
    listings = Property.objects.filter(review_status=Property.Review.APPROVED, is_archived=False).select_related("owner", "owner__profile")
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
    return render(request, "marketplace/properties.html", {
        "listings": listings, "q": q, "city": city, "kind": kind, "purpose": purpose,
        "types": Property.Type.choices, "purposes": Property.Purpose.choices,
    })


def property_detail(request, slug):
    prop = get_object_or_404(Property.objects.select_related("owner", "owner__profile"), slug=slug)
    is_owner_or_staff = request.user.is_authenticated and (request.user == prop.owner or request.user.is_staff)
    if prop.is_archived and not is_owner_or_staff:
        from django.http import Http404
        raise Http404("Property not found")
    if prop.review_status != Property.Review.APPROVED and not is_owner_or_staff:
        from django.http import Http404
        raise Http404("Property not found")
    form = EnquiryForm()
    is_saved = request.user.is_authenticated and SavedProperty.objects.filter(user=request.user, property=prop).exists()
    return render(request, "marketplace/property_detail.html", {
        "property": prop, "enquiry_form": form, "is_saved": is_saved,
        "realtor_profile": getattr(getattr(prop.owner, "profile", None), "role", None) == Profile.Role.REALTOR,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.email = form.cleaned_data["email"]
        user.is_active = True
        user.save()
        Profile.objects.create(
            user=user, role=form.cleaned_data["role"],
            phone=form.cleaned_data.get("phone", ""), city=form.cleaned_data.get("city", ""),
        )
        login(request, user)
        messages.success(request, "Your account is ready. Welcome to Urbisora Africa.")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    mine = Property.objects.filter(owner=request.user).order_by("-updated_at")
    incoming = Enquiry.objects.filter(property__owner=request.user).select_related("property")[:20]
    saved = SavedProperty.objects.filter(user=request.user).select_related("property", "property__owner")[:8]
    applications = RealtorApplication.objects.filter(user=request.user)
    approved_count = mine.filter(review_status=Property.Review.APPROVED, is_archived=False).count()
    pending_count = mine.filter(review_status=Property.Review.PENDING).count()
    new_enquiries = Enquiry.objects.filter(property__owner=request.user, status=Enquiry.Status.NEW).count()
    profile_fields = [profile.photo, profile.bio, profile.phone, profile.city, profile.specialties, profile.service_areas]
    completeness = int(sum(bool(value) for value in profile_fields) / len(profile_fields) * 100)
    return render(request, "marketplace/dashboard.html", {
        "profile": profile, "mine": mine, "incoming": incoming, "saved": saved, "applications": applications,
        "approved_count": approved_count, "pending_count": pending_count, "new_enquiries": new_enquiries,
        "profile_completeness": completeness,
    })


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile, account_user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your professional profile has been updated.")
        return redirect("dashboard")
    return render(request, "marketplace/profile_edit.html", {"form": form, "profile": profile})


def realtor_directory(request):
    profiles = Profile.objects.filter(role=Profile.Role.REALTOR).filter(
        Q(is_verified=True) | Q(user__realtor_applications__status=RealtorApplication.Status.APPROVED)
    ).select_related("user").distinct().annotate(
        active_listing_count=Count("user__properties", filter=Q(user__properties__review_status=Property.Review.APPROVED, user__properties__is_archived=False))
    ).order_by("-is_verified", "user__first_name")
    return render(request, "marketplace/realtors.html", {"profiles": profiles})


def realtor_profile(request, username):
    profile = get_object_or_404(
        Profile.objects.select_related("user"),
        user__username=username,
        role=Profile.Role.REALTOR,
    )
    if not profile.is_verified and not profile.user.realtor_applications.filter(status=RealtorApplication.Status.APPROVED).exists():
        from django.http import Http404
        raise Http404("Realtor profile not found")
    listings = Property.objects.filter(
        owner=profile.user, review_status=Property.Review.APPROVED, is_archived=False
    ).order_by("-created_at")
    return render(request, "marketplace/realtor_profile.html", {
        "profile": profile, "listings": listings,
        "listing_count": listings.count(),
    })


@login_required
def property_create(request):
    form = PropertyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        prop = form.save(commit=False)
        prop.owner = request.user
        prop.review_status = Property.Review.PENDING
        prop.is_archived = False
        prop.save()
        messages.success(request, "Your property was added to your workspace and sent for review.")
        return redirect("dashboard")
    return render(request, "marketplace/property_form.html", {"form": form, "editing": False})


@login_required
def property_edit(request, slug):
    prop = get_object_or_404(Property, slug=slug, owner=request.user)
    form = PropertyForm(request.POST or None, instance=prop)
    if request.method == "POST" and form.is_valid():
        prop = form.save(commit=False)
        prop.review_status = Property.Review.PENDING
        prop.save()
        messages.success(request, "Your changes have been saved and sent for review before republishing.")
        return redirect("dashboard")
    return render(request, "marketplace/property_form.html", {"form": form, "editing": True, "property": prop})


@login_required
@require_POST
def property_archive(request, slug):
    prop = get_object_or_404(Property, slug=slug, owner=request.user)
    prop.is_archived = not prop.is_archived
    prop.save(update_fields=["is_archived", "updated_at"])
    messages.success(request, "Property archived from public search." if prop.is_archived else "Property restored to your workspace; it still must be approved before public listing.")
    return redirect("dashboard")


@require_POST
def send_enquiry(request, slug):
    prop = get_object_or_404(Property, slug=slug, review_status=Property.Review.APPROVED, is_archived=False)
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
def enquiry_update(request, enquiry_id):
    enquiry = get_object_or_404(Enquiry.objects.select_related("property"), pk=enquiry_id, property__owner=request.user)
    status = request.POST.get("status")
    valid_statuses = {choice[0] for choice in Enquiry.Status.choices}
    if status in valid_statuses:
        enquiry.status = status
        enquiry.save(update_fields=["status"])
        messages.success(request, "Enquiry status updated.")
    else:
        messages.error(request, "Choose a valid enquiry status.")
    return redirect("dashboard")


@login_required
@require_POST
def toggle_saved(request, slug):
    prop = get_object_or_404(Property, slug=slug, review_status=Property.Review.APPROVED, is_archived=False)
    item, created = SavedProperty.objects.get_or_create(user=request.user, property=prop)
    if not created:
        item.delete()
        messages.info(request, "Property removed from your saved list.")
    else:
        messages.success(request, "Property saved to your list.")
    return redirect("property_detail", slug=slug)


@login_required
def realtor_apply(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    approved_application = RealtorApplication.objects.filter(user=request.user, status=RealtorApplication.Status.APPROVED).first()
    if approved_application:
        profile.role = Profile.Role.REALTOR
        profile.years_experience = approved_application.years_experience
        profile.save(update_fields=["role", "years_experience"])
        messages.info(request, "Your realtor membership is already active. Complete your professional profile to showcase your experience and properties.")
        return redirect("profile_edit")
    form = RealtorApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        app = RealtorApplication.objects.filter(user=request.user, status=RealtorApplication.Status.PENDING).first()
        if app is None:
            app = form.save(commit=False)
            app.user = request.user
        else:
            app.message = form.cleaned_data["message"]
            app.years_experience = form.cleaned_data["years_experience"]
            app.licence_or_company = form.cleaned_data["licence_or_company"]
        app.status = RealtorApplication.Status.APPROVED
        app.save()
        profile.role = Profile.Role.REALTOR
        profile.years_experience = app.years_experience
        profile.professional_title = profile.professional_title or "Real Estate Professional"
        profile.save()
        messages.success(request, "Your realtor membership is approved. Add your photo, professional experience and contact preferences to complete your public profile.")
        return redirect("profile_edit")
    return render(request, "marketplace/realtor_apply.html", {"form": form})


def contact(request):
    form = ContactMessageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Thank you for contacting Urbisora Africa. Your message has been recorded.")
        return redirect("contact")
    return render(request, "marketplace/contact.html", {
        "form": form,
        "contact_phone_display": "+234 906 791 2928",
        "contact_phone_link": "+2349067912928",
        "contact_email": "admin@ubisoraafrica.com",
        "contact_address": "Guzape, FCT Abuja, Federal Housing Authority (FHA) Road, 219 House 15",
        "powered_by": "Fortitech Digital Cluster",
    })
