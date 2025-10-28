# 🎯 Quick Reference: Exchange Application Controls

## Dashboard View

```
┌────────────────────────────────────────────────────────────────┐
│ Exchange Program Dashboard                                     │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ 📄 Exchange Application Form                            │  │
│ │                                                          │  │
│ │ ✅ Accepting Applications                               │  │
│ │ Students can now submit exchange applications.          │  │
│ │                                                          │  │
│ │        [🔗 Open Form] [📋 Copy Link] [🔴 Disable]       │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Quick Actions

| Button | Icon | Action | Result |
|--------|------|--------|--------|
| **Open Form** | 🔗 | Opens application form in new tab | Preview or share form directly |
| **Copy Link** | 📋 | Copies URL to clipboard | Quick sharing via email/chat |
| **Enable** | 🟢 | Turns on applications | Students can submit applications |
| **Disable** | 🔴 | Turns off applications | Shows closure message to students |

## Status Indicators

### ✅ Applications OPEN
- **Badge:** Green "Accepting Applications"
- **Button:** Red "Disable Applications"
- **Form:** Fully functional
- **Students:** Can submit applications

### ❌ Applications CLOSED
- **Badge:** Red "Applications Closed"
- **Button:** Green "Enable Applications"
- **Form:** Shows closure message
- **Students:** See "check back later" message

## Copy Link Behavior

```
1. Click "Copy Link"
   ↓
2. Button turns green
   ↓
3. Shows "Copied!" (2 seconds)
   ↓
4. Reverts to blue outline
   ↓
5. Link is in clipboard, ready to paste
```

## Student Experience

### When ENABLED
```
Student clicks link
    ↓
Form loads normally
    ↓
Student fills and submits
    ↓
Success! Email sent with next steps
```

### When DISABLED
```
Student clicks link
    ↓
⚠️ Warning message displayed
    ↓
"Applications currently closed"
    ↓
[Back to Exchange Program] button
```

## Database Fields

```python
ExchangeProgramSettings:
  - applications_enabled (Boolean)     # True = Open, False = Closed
  - applications_closed_message (Text) # Custom message when closed
  - last_updated (DateTime)            # Auto-timestamp
  - updated_by (User)                  # Who made the change
```

## Migration

```bash
# Apply migration
python manage.py migrate

# Verify
python manage.py showmigrations main
# Should show:
# [X] 0032_exchangeprogramsettings_applications_closed_message_and_more
```

## Code Locations

| Feature | File | Line |
|---------|------|------|
| Model fields | `main/models.py` | ~277 |
| Toggle handler | `main/views.py` | ~877 |
| Gate check | `main/views.py` | ~743 |
| Dashboard UI | `exchange_dashboard.html` | ~31 |
| Form closure | `exchange_application.html` | ~18 |
| Copy JS | `exchange_dashboard.html` | ~62 |

## Testing Commands

```python
# Test in Django shell
python manage.py shell

from main.models import ExchangeProgramSettings

# Get settings
settings = ExchangeProgramSettings.get_settings()

# Check status
print(settings.applications_enabled)  # True or False

# Enable applications
settings.applications_enabled = True
settings.save()

# Disable applications
settings.applications_enabled = False
settings.save()

# View closure message
print(settings.applications_closed_message)
```

## Common Use Cases

### 1️⃣ Open Applications for New Semester
```
1. Navigate to Dashboard
2. Click "Enable Applications" (green button)
3. Click "Copy Link"
4. Email link to partner universities
```

### 2️⃣ Share Link Quickly
```
1. Navigate to Dashboard
2. Click "Copy Link"
3. Button shows "Copied!"
4. Paste in email/announcement
```

### 3️⃣ Close After Deadline
```
1. Navigate to Dashboard
2. Click "Disable Applications" (red button)
3. Confirm in success message
4. Students now see closure message
```

### 4️⃣ Preview Form
```
1. Navigate to Dashboard
2. Click "Open Form" button
3. New tab opens with form
4. Works even when disabled
```

## URL Structure

```
Application URL:
https://yourdomain.com/exchange/application/

Dashboard URL:
https://yourdomain.com/portal/exchange-dashboard/
```

## Permissions

| Action | Public | Exchange Officer | Admin |
|--------|--------|------------------|-------|
| View Dashboard | ❌ | ✅ | ✅ |
| Toggle Applications | ❌ | ✅ | ✅ |
| Copy Link | ❌ | ✅ | ✅ |
| View Form (Enabled) | ✅ | ✅ | ✅ |
| View Closure (Disabled) | ✅ | ✅ | ✅ |
| Submit Application (Enabled) | ✅ | ✅ | ✅ |
| Submit Application (Disabled) | ❌ | ❌ | ❌ |

## Success Messages

```
✅ "Exchange applications have been enabled."
✅ "Exchange applications have been disabled."
✅ Link copied to clipboard (visual feedback)
```

## Error Prevention

- ✅ CSRF token protection on toggle
- ✅ Permission checks on POST
- ✅ Singleton pattern prevents duplicates
- ✅ Form hidden when disabled (not just disabled)
- ✅ Clear error messages
- ✅ Back button when closed

## Tips

💡 **For Quick Sharing:** Use Copy Link button - it's faster and error-free

💡 **For Testing:** Open Form button works even when disabled for preview

💡 **For Planning:** Update closure message before disabling to inform students

💡 **For Tracking:** Check `updated_by` and `last_updated` fields in admin

## Visual Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Exchange Officer                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Exchange Dashboard          │
        └───────────────┬───────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐              ┌────────────────┐
│ Enable Apps   │              │  Copy Link     │
└───────┬───────┘              └────────┬───────┘
        │                               │
        ▼                               ▼
┌───────────────────┐          ┌─────────────────┐
│ Applications OPEN │          │ Share with      │
│ Students can      │          │ Partners        │
│ submit forms      │          │                 │
└───────────────────┘          └─────────────────┘
```

## Summary

✨ **3 Main Features:**
1. **Toggle** - Enable/Disable applications instantly
2. **Open Form** - Quick access to application form
3. **Copy Link** - One-click URL copying

✨ **2 User States:**
1. **Enabled** - Form works, applications accepted
2. **Disabled** - Closure message shown, form hidden

✨ **1 Location:**
- All controls in Exchange Dashboard, top card

**Status:** ✅ Complete and ready to use!
