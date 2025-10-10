# Export Attendance by Section Feature

## Overview
Members can now export event attendance data organized by sections as Excel files. Each section gets its own professionally formatted Excel file, and all files are delivered in a single ZIP download.

## How to Use

### 1. Access Events Dashboard
- Log in as a member, staff, or superuser
- Navigate to: **Portal → Events Dashboard**

### 2. View Event Attendance
- Click on any event card to open the attendance modal
- The modal shows all registered attendees and their attendance status

### 3. Export by Section
- Click the **"Export by Section"** button (green button with Excel icon) in the modal header
- A ZIP file will be downloaded containing one Excel file per section

### 4. Open the ZIP File
- Extract the ZIP file to see individual Excel files
- Each file is named: `[Section_Code]_[Professor_Name].xlsx`

## File Structure

### ZIP File Contents
Example: `Event_Name_Attendance_by_Section.zip`
```
├── SEC01_Prof_Smith.xlsx
├── SEC02_Prof_Jones.xlsx
├── LAB01_Dr_Ahmed.xlsx
└── TUT01_TA_Sarah.xlsx
```

### Excel File Format
Each Excel file contains:

**Row 1: Event Title**
- Merged header with event name: "Event Title - Attendance Report"
- Dark blue background, white text, centered

**Row 2: Section Information**
- Section code and professor name: "Section: SEC01 - Professor: Dr. Smith"
- Light blue background, white text, centered

**Row 3: Event Date**
- Event date(s): "Event Date: 2025-10-15 to 2025-10-17"
- Gray italic text, centered

**Row 5: Column Headers**
1. **Student ID** - Student's ID number
2. **Student Name** - Full name
3. **Email** - Student email address
4. **Attended Start** - "Yes" (green) or "No" (red)
5. **Attended End** - "Yes" (green) or "No" (red)

**Data Rows (6+):**
- One row per student in that section
- Bordered cells for easy reading
- Color-coded Yes/No values:
  - ✓ **"Yes"** in green (attended)
  - ✗ **"No"** in red (absent)

**Summary Row:**
- Total student count at the bottom

## Features

### Professional Formatting
- ✅ Color-coded headers (dark blue, light blue)
- ✅ Bordered cells for clarity
- ✅ Auto-sized columns for readability
- ✅ Color-coded attendance status (green/red)
- ✅ Bold headers and summary text
- ✅ Centered alignment for status columns

### Data Organization
- ✅ One Excel file per section
- ✅ Students sorted alphabetically by name
- ✅ Only includes students registered for that specific section
- ✅ All files bundled in a single ZIP download

### File Naming
- ✅ Safe filenames (removes special characters)
- ✅ Descriptive names with section code and professor
- ✅ ZIP file named after event title

## Use Cases

### 1. Share with Professors
After an event, export attendance and email each professor their section's file:
```
Email to Prof. Smith:
Subject: SEC01 Attendance - Event Name
Attachment: SEC01_Prof_Smith.xlsx
```

### 2. Bonus Points Tracking
Professors can use the Excel files to:
- Import into their gradebook systems
- Track which students attended both start and end
- Award bonus points based on attendance

### 3. Administrative Records
Keep organized records of attendance by section:
- Archive files for future reference
- Generate reports for department
- Verify student participation

### 4. Event Analysis
Analyze attendance patterns:
- Which sections had highest attendance?
- Start vs. end attendance rates
- Section-specific engagement metrics

## Excel File Example

```
╔══════════════════════════════════════════════════════════════════════╗
║           Event Title - Attendance Report                            ║
╠══════════════════════════════════════════════════════════════════════╣
║           Section: SEC01 - Professor: Dr. John Smith                 ║
╠══════════════════════════════════════════════════════════════════════╣
║           Event Date: 2025-10-15 to 2025-10-17                       ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
╠════════════╦══════════════════╦══════════════════╦═══════════╦══════╣
║ Student ID ║  Student Name    ║     Email        ║  Start    ║ End  ║
╠════════════╬══════════════════╬══════════════════╬═══════════╬══════╣
║ 202100001  ║ Ahmed Hassan     ║ ahmed@uni.edu    ║  Yes ✓    ║ Yes ✓║
║ 202100002  ║ Fatima Khalid    ║ fatima@uni.edu   ║  Yes ✓    ║ No ✗ ║
║ 202100003  ║ Omar Yousef      ║ omar@uni.edu     ║  No ✗     ║ Yes ✓║
║ 202100004  ║ Sara Ahmed       ║ sara@uni.edu     ║  Yes ✓    ║ Yes ✓║
╠════════════╩══════════════════╩══════════════════╩═══════════╩══════╣
║ Total Students: 4                                                    ║
╚══════════════════════════════════════════════════════════════════════╝
```

## Technical Details

### Export Format
- **File Type**: Excel (.xlsx) using openpyxl
- **Compression**: ZIP format for multiple files
- **Encoding**: UTF-8 for international characters

### Column Widths
- Student ID: 15 characters
- Student Name: 30 characters
- Email: 30 characters
- Attended Start: 18 characters
- Attended End: 18 characters

### Styling
- Headers: White text on dark blue (#34495E)
- Section info: White text on light blue (#3498DB)
- Yes: Bold green text (#27AE60)
- No: Bold red text (#E74C3C)
- Borders: Thin black lines on all data cells

### Performance
- Efficient query using Django ORM with section filtering
- In-memory ZIP creation (no temporary files)
- Instant download via HTTP response

## Requirements

### Prerequisites
- Event must have sections created (via "Manage Sections")
- Students must have selected sections during end attendance
- User must be authenticated member/staff/superuser

### Dependencies
- `openpyxl==3.1.5` (already in requirements.txt)
- Built-in Python `zipfile` module
- Django's `HttpResponse` for file downloads

## Error Handling

### No Sections Found
If an event has no sections configured:
```
Error: "No sections found for this event."
Redirects back to events dashboard
```

### Permission Denied
If non-member tries to export:
```
Error: "You do not have permission to export attendance data."
Redirects to events dashboard
```

### Export Failure
If export process fails:
```
Error: "Error exporting attendance data: [details]"
Redirects to events dashboard
```

## Tips

1. **Create Sections First**: Use "Manage Sections" button on event detail page
2. **Students Select Sections**: During end attendance verification
3. **Multiple Downloads**: You can export multiple times without issues
4. **Share Selectively**: Extract ZIP and send individual files to professors
5. **Keep Records**: Archive ZIP files for institutional records

## Future Enhancements

Potential improvements:
- Export all events at once (bulk export)
- Export single event with all sections in one Excel file (multiple sheets)
- Custom column selection (filter which fields to include)
- PDF format option for printing
- Email integration (automatically send files to professors)
- Attendance statistics dashboard per section

## Support

For issues or questions:
1. Verify sections are created for the event
2. Ensure students selected sections during end attendance
3. Check that you have member/staff permissions
4. Contact system administrator if problems persist
