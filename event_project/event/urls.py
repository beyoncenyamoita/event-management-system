from django.urls import path
from . import views

urlpatterns = [
    # Template URLs
    path('', views.HomePageView.as_view(), name='home'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('event/<int:event_id>/register/', views.RegistrationCreateView.as_view(), name='register_event'),
    
    # API URLs (Pure Django)
    path('api/events/', views.event_list_api, name='api_event_list'),
    path('api/events/<int:pk>/', views.event_detail_api, name='api_event_detail'),
    path('api/registrations/', views.registration_list_api, name='api_registration_list'),
]