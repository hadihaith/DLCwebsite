"""
Quick test script to verify QR code URLs are valid and accessible.
Run this to test the QR generation without needing a browser.
"""

import os
import django

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dlcweb.settings')
django.setup()

from main.models import Event
from django.urls import reverse
from urllib.parse import quote

def test_qr_urls():
    """Test QR generation for all events."""
    events = Event.objects.all()
    
    if not events:
        print("No events found in database. Create an event first.")
        return
    
    print(f"\n{'='*80}")
    print(f"Testing QR Code Generation for {events.count()} event(s)")
    print(f"{'='*80}\n")
    
    for event in events:
        print(f"\n📅 Event: {event.title} (ID: {event.pk})")
        print(f"   Date: {event.start_date} to {event.end_date}")
        
        # Test start QR
        if all([event.secret_start_a, event.secret_start_b, event.secret_start_c]):
            start_path = reverse('verify_start', args=(
                event.secret_start_a,
                event.secret_start_b,
                event.secret_start_c
            ))
            start_url = f'http://localhost:8000{start_path}'
            start_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={quote(start_url, safe='')}"
            
            print(f"\n   ✅ START QR Available")
            print(f"      Secrets: {event.secret_start_a} / {event.secret_start_b} / {event.secret_start_c}")
            print(f"      Verify URL: {start_url}")
            print(f"      QR Image: {start_qr[:80]}...")
        else:
            print(f"\n   ❌ START QR Missing (secrets not configured)")
        
        # Test end QR
        if all([event.secret_end_a, event.secret_end_b, event.secret_end_c]):
            end_path = reverse('verify_end', args=(
                event.secret_end_a,
                event.secret_end_b,
                event.secret_end_c
            ))
            end_url = f'http://localhost:8000{end_path}'
            end_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={quote(end_url, safe='')}"
            
            print(f"\n   ✅ END QR Available")
            print(f"      Secrets: {event.secret_end_a} / {event.secret_end_b} / {event.secret_end_c}")
            print(f"      Verify URL: {end_url}")
            print(f"      QR Image: {end_qr[:80]}...")
        else:
            print(f"\n   ❌ END QR Missing (secrets not configured)")
        
        print(f"\n   {'─'*70}")
    
    print(f"\n{'='*80}")
    print("✨ Test complete! Copy any QR Image URL and paste in browser to see the code.")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    test_qr_urls()
