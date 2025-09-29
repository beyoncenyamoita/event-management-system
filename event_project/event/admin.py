from django.contrib import admin
from .models import Event, Registration

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location', 'max_attendees', 'available_spots', 'is_full']
    list_filter = ['date', 'location']
    search_fields = ['title', 'description']
    date_hierarchy = 'date'

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'event', 'registered_at']
    list_filter = ['event', 'registered_at']
    search_fields = ['first_name', 'last_name', 'email', 'event__title']
    date_hierarchy = 'registered_at'