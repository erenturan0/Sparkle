from django.urls import path
from . import views

app_name = "smart_home"

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.dashboard, name='dashboard'),

    path('devices/', views.devices_list, name='devices'),
    path('devices/add/', views.device_add, name='device_add'),
    path('devices/<int:device_id>/edit/', views.device_edit, name='device_edit'),
    path('devices/<int:device_id>/delete/', views.device_delete, name='device_delete'),

    path('settings/', views.settings_view, name='settings'),
    path('settings/profile/', views.settings_profile, name='settings_profile'),
    path('settings/password/', views.settings_password, name='settings_password'),

    path('requests/', views.share_requests, name='share_requests'),
    path('requests/<int:request_id>/approve/', views.share_request_approve, name='share_request_approve'),
    path('requests/<int:request_id>/reject/', views.share_request_reject, name='share_request_reject'),

    path('api/toggle/<int:device_id>/', views.api_toggle, name='api_toggle'),
]
