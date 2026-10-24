from django.urls import path
from . import views, ai_views

urlpatterns = [
    path("", views.home, name="home"),
    path("properties/", views.property_list, name="property_list"),
    path("properties/new/", views.property_create, name="property_create"),
    path("properties/<slug:slug>/edit/", views.property_edit, name="property_edit"),
    path("properties/<slug:slug>/archive/", views.property_archive, name="property_archive"),
    path("properties/<slug:slug>/", views.property_detail, name="property_detail"),
    path("properties/<slug:slug>/enquire/", views.send_enquiry, name="send_enquiry"),
    path("properties/<slug:slug>/save/", views.toggle_saved, name="toggle_saved"),
    path("enquiries/<int:enquiry_id>/update/", views.enquiry_update, name="enquiry_update"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("realtors/", views.realtor_directory, name="realtors"),
    path("realtors/apply/", views.realtor_apply, name="realtor_apply"),
    path("realtors/<str:username>/message/", views.realtor_lead_submit, name="realtor_lead_submit"),
    path("realtors/<str:username>/", views.realtor_profile, name="realtor_profile"),
    path("realtor-leads/<int:lead_id>/update/", views.realtor_lead_update, name="realtor_lead_update"),
    path("contact/", views.contact, name="contact"),
    path("ai/chat/", ai_views.chat, name="ai_chat"),
    path("ai/action/", ai_views.action, name="ai_action"),
]
