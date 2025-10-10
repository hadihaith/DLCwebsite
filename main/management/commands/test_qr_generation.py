"""
Management command to test QR code generation for events.
Usage: python manage.py test_qr_generation <event_id>
"""
from django.core.management.base import BaseCommand
from django.urls import reverse
from main.models import Event
from urllib.parse import quote


class Command(BaseCommand):
    help = 'Test QR code generation for an event'

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, help='Event ID to test')

    def handle(self, *args, **options):
        event_id = options['event_id']
        
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Event with ID {event_id} not found'))
            return

        self.stdout.write(self.style.SUCCESS(f'\n=== Event: {event.title} ==='))
        
        # Check start secrets
        if event.secret_start_a and event.secret_start_b and event.secret_start_c:
            self.stdout.write(f'\nStart secrets: {event.secret_start_a}, {event.secret_start_b}, {event.secret_start_c}')
            start_path = reverse('verify_start', args=(event.secret_start_a, event.secret_start_b, event.secret_start_c))
            # In production, this would be a full URL like https://yourdomain.com/events/verify/start/...
            start_url = f'http://localhost:8000{start_path}'
            encoded_start = quote(start_url, safe='')
            start_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_start}"
            
            self.stdout.write(f'Start URL: {start_url}')
            self.stdout.write(f'Start QR image: {start_qr}')
        else:
            self.stdout.write(self.style.WARNING('\nStart secrets not configured'))
        
        # Check end secrets
        if event.secret_end_a and event.secret_end_b and event.secret_end_c:
            self.stdout.write(f'\nEnd secrets: {event.secret_end_a}, {event.secret_end_b}, {event.secret_end_c}')
            end_path = reverse('verify_end', args=(event.secret_end_a, event.secret_end_b, event.secret_end_c))
            end_url = f'http://localhost:8000{end_path}'
            encoded_end = quote(end_url, safe='')
            end_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_end}"
            
            self.stdout.write(f'End URL: {end_url}')
            self.stdout.write(f'End QR image: {end_qr}')
        else:
            self.stdout.write(self.style.WARNING('\nEnd secrets not configured'))
        
        self.stdout.write(self.style.SUCCESS('\n\nYou can test the QR codes by:'))
        self.stdout.write('1. Opening the QR image URLs in a browser to see the QR codes')
        self.stdout.write('2. Scanning them with a phone camera')
        self.stdout.write('3. Or visiting the verify URLs directly\n')
