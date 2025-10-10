# Events Dashboard - DLC Portal

## Overview
A comprehensive events management dashboard for DLC members to view all events and track attendance in real-time.

## Features

### 📊 Dashboard Overview
- **Grid view** of all events with visual status indicators
- **Filter by status**: All, Upcoming, Ongoing, Past
- **Quick statistics** for each event:
  - Total registrations
  - Start attendance count
  - End attendance count
- **Color-coded status badges**:
  - 🔵 **Upcoming** - Events that haven't started yet
  - 🟢 **Ongoing** - Events happening now
  - 🔴 **Past** - Completed events

### 👥 Attendance Tracking
Click any event card to view detailed attendance information:

#### Stats Summary
- Total registered students
- Students who attended start only
- Students who attended end only  
- Students who attended both

#### Filter Tabs
- **All Registrations** - Everyone who registered
- **Start Attendance** - Students who checked in at start
- **End Attendance** - Students who checked in at end
- **Both Attended** - Students who checked in for both

#### Attendance Table
View complete details for each student:
- Student ID
- Student Name
- Email
- Attendance Code
- Start attendance status (✓ Present / ✗ Absent)
- End attendance status (✓ Present / ✗ Absent)

#### Search Functionality
Real-time search through attendance records by:
- Student name
- Student ID
- Email

### 🎯 Quick Actions
From each event card:
- **View Event** - Go to public event detail page
- **QR Codes** - Access start/end QR codes for attendance

## Access

### Who Can Access
- ✅ Members (is_member = True)
- ✅ Staff users
- ✅ Superusers

### Device Requirements
- Desktop or laptop only
- Mobile/tablet devices are redirected with an appropriate message

## URLs

- **Dashboard**: `/portal/events-dashboard`
- **Attendance API**: `/portal/events/<event_id>/attendance-data/?filter=<all|start|end|both>`

## Navigation

Access the dashboard from the portal sidebar:
**Tools → Events Dashboard**

## Technical Details

### Views

#### `events_dashboard(request)`
- Lists all events with computed statistics
- Determines event status (upcoming/ongoing/past)
- Counts attendance for start and end
- Member-only access with device restrictions

#### `event_attendance_data(request, pk)`
- JSON API endpoint for attendance data
- Accepts filter parameter (all, start, end, both)
- Returns statistics and filtered attendance list
- Member-only access

### Database Queries
Optimized to:
1. Load all events ordered by start date
2. Count attendances per event
3. Filter attendances based on user selection
4. No N+1 query problems

### Frontend
- **Responsive grid layout** (auto-fill, min 350px)
- **Modal popup** for attendance details
- **AJAX requests** for dynamic data loading
- **No page refresh** when viewing different events
- **Real-time search filtering** with JavaScript

## Status Determination Logic

```python
if event.end_date < today:
    status = 'past'
elif event.start_date > today:
    status = 'upcoming'
else:
    status = 'ongoing'
```

## Statistics Calculation

```python
total = all attendances for event
start_only = present_start=True AND present_end=False
end_only = present_start=False AND present_end=True
both = present_start=True AND present_end=True
```

## User Experience Flow

1. **Member logs in** → Portal
2. **Clicks "Events Dashboard"** in sidebar
3. **Sees all events** in grid view
4. **Filters by status** (optional)
5. **Clicks event card** → Modal opens
6. **Views attendance statistics**
7. **Switches between tabs** to filter attendance
8. **Searches for specific student** (optional)
9. **Clicks "View Event"** or "QR Codes"** for actions

## Security

- ✅ Login required decorator
- ✅ Member/staff/superuser permission check
- ✅ Device type validation (desktop only)
- ✅ GET parameter validation for filters
- ✅ Event existence validation (404 if not found)

## Future Enhancements

- [ ] Export attendance to CSV/Excel
- [ ] Email attendance reports to organizers
- [ ] Attendance rate analytics and charts
- [ ] Historical comparison between events
- [ ] Automated attendance reminders
- [ ] Bulk attendance updates
- [ ] Event templates for quick creation
- [ ] Integration with calendar apps

## Testing

### Manual Test Steps
1. Login as a member
2. Navigate to `/portal/events-dashboard`
3. Verify all events are displayed
4. Test filter dropdown
5. Click an event card
6. Verify modal opens with correct data
7. Test tab switching (All, Start, End, Both)
8. Test search functionality
9. Verify "View Event" and "QR Codes" links work

### Test Data Required
- At least one event with:
  - Multiple registrations
  - Some with start attendance marked
  - Some with end attendance marked
  - Some with both marked

## Troubleshooting

**Events not showing?**
- Check if events exist in database
- Verify user has member permissions

**Modal not loading data?**
- Check browser console for JavaScript errors
- Verify API endpoint is accessible
- Check network tab for failed requests

**Search not working?**
- Clear browser cache
- Check if JavaScript is enabled
- Look for console errors

**Styling issues?**
- All styles are embedded in the template
- No external CSS dependencies required
