from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("properties/", views.property_list, name="property_list"),
    path("properties/new/", views.property_create, name="property_create"),
    path("properties/<slug:slug>/", views.property_detail, name="property_detail"),
    path("properties/<slug:slug>/enquire/", views.send_enquiry, name="send_enquiry"),
    path("properties/<slug:slug>/save/", views.toggle_saved, name="toggle_saved"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("realtors/", views.realtor_directory, name="realtors"),
    path("realtors/apply/", views.realtor_apply, name="realtor_apply"),
]
