# DLC Attendance QR Code System

## Overview
The attendance system now automatically generates secret numbers for each event and creates QR codes that encode verification URLs.

## How It Works

### 1. Automatic Secret Generation
When an event is created, the system automatically generates 6 random numbers:
- **Start attendance**: 3 six-digit numbers (secret_start_a, secret_start_b, secret_start_c)
- **End attendance**: 3 six-digit numbers (secret_end_a, secret_end_b, secret_end_c)

Each number is between 100,000 and 999,999.

### 2. QR Code Generation
Members can access the QR codes for any event by:
1. Going to the event detail page
2. Clicking "Get attendance QR code"
3. Choosing to display either the start or end QR code

The QR codes are generated using Google Charts API (no external libraries required).

### 3. Verification Flow
1. **Attendee scans QR code** → taken to verify page with the event's secret numbers in the URL
2. **Attendee enters their 6-digit attendance code** → the code they received when registering
3. **System verifies the code** → checks if it matches an attendance record for that event
4. **System checks timing**:
   - For start attendance: event must have started
   - For end attendance: event must have ended
5. **System marks attendance** → sets present_start or present_end to True

## Technical Implementation

### QR Code API
We use **api.qrserver.com** (formerly known as goQR.me) for QR code generation:
- **Free and reliable** - No API key required
- **Simple REST API** - Just pass the URL as a parameter
- **Better than Google Charts** - Google's QR API was deprecated in 2012

### Model Changes (main/models.py)
```python
# Event model now auto-generates secrets in save() method
def save(self, *args, **kwargs):
    if not self.pk:  # New event
        if self.secret_start_a is None:
            self.secret_start_a, self.secret_start_b, self.secret_start_c = self._generate_triplet()
        if self.secret_end_a is None:
            self.secret_end_a, self.secret_end_b, self.secret_end_c = self._generate_triplet()
    super().save(*args, **kwargs)
```

### View: attendance_qr (main/views.py)
Builds URLs and generates QR codes:
```python
# Start URL example: /events/verify/start/636248/292432/469775/
# End URL example: /events/verify/end/283592/200350/257475/

# QR image URL (using api.qrserver.com):
https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=<encoded_url>
```

### Views: verify_start and verify_end (main/views.py)
Handle code submission and attendance marking:
- Accept three secret numbers as URL parameters
- Find the matching event
- Display form for code entry
- Validate code and timing
- Mark appropriate attendance boolean

## URLs
- `/events/<id>/attendance-qr/` - Member-only QR code display page
- `/events/verify/start/<a>/<b>/<c>/` - Start attendance verification
- `/events/verify/end/<a>/<b>/<c>/` - End attendance verification

## Security Features
- QR codes are only accessible to members (is_member, staff, or superuser)
- Secret numbers are randomly generated and unique to each event
- Attendance codes are unique per event
- Timing validation ensures start/end attendance is only marked at appropriate times

## Testing

### Command Line Test
```bash
py manage.py test_qr_generation <event_id>
```

This will display:
- The event's secret numbers
- The verification URLs
- The QR code image URLs

### Visual Test
Open `test_qr_visual.html` in a browser to see example QR codes and understand the workflow.

### Manual Test
1. Create a new event (secrets will be auto-generated)
2. Register for the event to get an attendance code
3. As a member, visit the event and click "Get attendance QR code"
4. Scan the QR code with your phone
5. Enter your attendance code
6. Verify the attendance was marked in the admin panel

## Example
For event ID 6 ("sssss"):
- **Start secrets**: 636248, 292432, 469775
- **End secrets**: 283592, 200350, 257475
- **Start QR URL**: http://localhost:8000/events/verify/start/636248/292432/469775/
- **End QR URL**: http://localhost:8000/events/verify/end/283592/200350/257475/

## Alternative QR Solutions (if needed)

If api.qrserver.com is unavailable, you can switch to:

1. **Local generation with Python** (requires `pip install qrcode[pil]`):
```python
import qrcode
from io import BytesIO
import base64

def generate_qr_data_url(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"
```

2. **Other free APIs**:
   - `https://quickchart.io/qr?text={url}&size=300`
   - `https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={url}` (deprecated but may still work)

## Future Enhancements
- [ ] Admin interface to regenerate/rotate secret numbers
- [ ] Downloadable QR code images
- [ ] Print-friendly QR code sheets
- [ ] Analytics on QR code scans
- [ ] Fallback QR generation if API is down
