from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Event, Registration

# Template Views
class HomePageView(ListView):
    model = Event
    template_name = 'event/home.html'  # Changed from 'events/home.html'
    context_object_name = 'events'
    
    def get_queryset(self):
        return Event.objects.all().order_by('date')

class EventDetailView(DetailView):
    model = Event
    template_name = 'event/event_detail.html'  # Changed from 'events/event_detail.html'
    context_object_name = 'event'

class RegistrationCreateView(CreateView):
    model = Registration
    template_name = 'event/registration_form.html'  # Changed from 'events/registration_form.html'
    fields = ['first_name', 'last_name', 'email', 'phone']
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        event = get_object_or_404(Event, pk=self.kwargs['event_id'])
        form.instance.event = event
        
        if event.is_full:
            form.add_error(None, 'This event is already full.')
            return self.form_invalid(form)
        
        if Registration.objects.filter(event=event, email=form.instance.email).exists():
            form.add_error('email', 'This email is already registered for this event.')
            return self.form_invalid(form)
            
        return super().form_valid(form)

# Pure Django API Views (keep the same as before)
def event_list_api(request):
    """API to get all events"""
    if request.method == 'GET':
        events = Event.objects.all().order_by('date')
        events_data = []
        
        for event in events:
            events_data.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'date': event.date.isoformat() if event.date else None,
                'location': event.location,
                'max_attendees': event.max_attendees,
                'available_spots': event.available_spots,
                'is_full': event.is_full,
                'created_at': event.created_at.isoformat(),
            })
        
        return JsonResponse(events_data, safe=False)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def event_detail_api(request, pk):
    """API to get specific event details"""
    if request.method == 'GET':
        try:
            event = Event.objects.get(pk=pk)
            event_data = {
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'date': event.date.isoformat() if event.date else None,
                'location': event.location,
                'max_attendees': event.max_attendees,
                'available_spots': event.available_spots,
                'is_full': event.is_full,
                'created_at': event.created_at.isoformat(),
            }
            return JsonResponse(event_data)
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def registration_list_api(request):
    """API to list registrations and create new ones"""
    if request.method == 'GET':
        registrations = Registration.objects.all()
        registrations_data = []
        
        for reg in registrations:
            registrations_data.append({
                'id': reg.id,
                'event': reg.event.id,
                'event_title': reg.event.title,
                'first_name': reg.first_name,
                'last_name': reg.last_name,
                'email': reg.email,
                'phone': reg.phone,
                'registered_at': reg.registered_at.isoformat(),
            })
        
        return JsonResponse(registrations_data, safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['event', 'first_name', 'last_name', 'email']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            
            # Get event
            try:
                event = Event.objects.get(pk=data['event'])
            except Event.DoesNotExist:
                return JsonResponse({'error': 'Event not found'}, status=404)
            
            # Check if event is full
            if event.is_full:
                return JsonResponse({'error': 'This event is already full.'}, status=400)
            
            # Check if email already registered
            if Registration.objects.filter(event=event, email=data['email']).exists():
                return JsonResponse({'error': 'This email is already registered for this event.'}, status=400)
            
            # Create registration
            registration = Registration.objects.create(
                event=event,
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data.get('phone', '')
            )
            
            # Return created registration
            response_data = {
                'id': registration.id,
                'event': registration.event.id,
                'event_title': registration.event.title,
                'first_name': registration.first_name,
                'last_name': registration.last_name,
                'email': registration.email,
                'phone': registration.phone,
                'registered_at': registration.registered_at.isoformat(),
                'message': 'Registration successful!'
            }
            
            return JsonResponse(response_data, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def api_documentation(request):
    """Simple API documentation page"""
    return render(request, 'event/api_docs.html')  # Changed from 'events/api_docs.html'