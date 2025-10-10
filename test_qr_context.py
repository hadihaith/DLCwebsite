import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dlcweb.settings')
django.setup()

from main.models import Event
from django.urls import reverse
from urllib.parse import quote

print("\n" + "="*80)
print("Testing QR Context Generation")
print("="*80 + "\n")

event = Event.objects.get(pk=6)
print(f"Event: {event.title} (ID: {event.pk})")
print(f"Start secrets exist: {bool(event.secret_start_a and event.secret_start_b and event.secret_start_c)}")
print(f"End secrets exist: {bool(event.secret_end_a and event.secret_end_b and event.secret_end_c)}")

# Simulate what the view does
start_ok = event.secret_start_a is not None and event.secret_start_b is not None and event.secret_start_c is not None
end_ok = event.secret_end_a is not None and event.secret_end_b is not None and event.secret_end_c is not None

start_url = None
end_url = None
if start_ok:
    start_url = f'http://localhost:8000{reverse("verify_start", args=(event.secret_start_a, event.secret_start_b, event.secret_start_c))}'
if end_ok:
    end_url = f'http://localhost:8000{reverse("verify_end", args=(event.secret_end_a, event.secret_end_b, event.secret_end_c))}'

def qr_img_url(target):
    encoded_target = quote(target, safe='')
    return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_target}"

context = {
    'event': event,
    'start_url': start_url,
    'end_url': end_url,
    'start_qr': qr_img_url(start_url) if start_url else None,
    'end_qr': qr_img_url(end_url) if end_url else None,
}

print("\n📦 Context being passed to template:")
print(f"   event: {context['event']}")
print(f"   start_url: {context['start_url']}")
print(f"   end_url: {context['end_url']}")
print(f"   start_qr: {context['start_qr'][:80] if context['start_qr'] else None}...")
print(f"   end_qr: {context['end_qr'][:80] if context['end_qr'] else None}...")

print("\n✅ Context looks good!")
print("\n" + "="*80 + "\n")
