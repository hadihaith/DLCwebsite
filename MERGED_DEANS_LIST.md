# Merged Dean's List Feature

## Overview
This feature allows administrators to view and compare Dean's List data from Fall and Spring semesters of the same academic year in a single, unified view.

## Access
- **URL**: `/portal/merged-deans-list/`
- **Route Name**: `merged_deans_list`
- **Permission**: President or Staff only

## Features

### 1. Year Selection
- Dropdown menu showing all available academic years from the database
- Years are sorted in descending order (most recent first)
- Automatically displays available years that have Dean's List data

### 2. Data Display
The merged view shows the following columns for each student:
- **Student ID**: Unique student identifier
- **Student Name**: Full name of the student
- **Major**: Academic major
- **GPA Fall**: GPA from Fall semester (shows "N/A" if not in Fall Dean's List)
- **GPA Spring**: GPA from Spring semester (shows "N/A" if not in Spring Dean's List)
- **Credits Passed Fall**: Credits passed in Fall (shows "N/A" if not available)
- **Credits Passed Spring**: Credits passed in Spring (shows "N/A" if not available)

### 3. Data Merging Logic
- Combines all students who appear in either Fall or Spring Dean's List for the selected year
- Students appearing in only one semester will show "N/A" for the missing semester's data
- Student name and major are taken from whichever semester has data available
- Students are sorted by Student ID for easy reference

### 4. Excel Export
- **Button**: "Export to Excel" (visible when data is available)
- **Filename**: `Deans_List_Merged_YYYY.xlsx` (where YYYY is the selected year)
- **Format**: Professional Excel spreadsheet with:
  - Styled headers (blue background, white text, bold, centered)
  - All student data in rows
  - Auto-adjusted column widths for readability
  - "N/A" values preserved in export

### 5. Statistics Cards
When data is available, the page displays:
- **Total Students**: Count of unique students across both semesters
- **Academic Year**: The selected year
- **Semesters**: Confirms "Fall & Spring" comparison

## Implementation Details

### Files Modified/Created

1. **main/views.py**
   - Added `merged_deans_list()` function
   - Queries DeanListStudent for Fall and Spring data
   - Merges data using dictionaries for efficient lookup
   - Handles Excel export using openpyxl

2. **main/urls.py**
   - Added route: `path('portal/merged-deans-list/', views.merged_deans_list, name='merged_deans_list')`

3. **main/templates/frontend/merged_deans_list.html**
   - New template with modern, responsive design
   - Year selector dropdown
   - Statistics cards
   - Data table with alternating row colors
   - Export button
   - Empty states for no selection or no data

4. **main/templates/frontend/portal.html**
   - Added menu link to "Merged Dean's List View" in the Tools section

### Dependencies
- **openpyxl**: Already included in requirements.txt (version 3.1.5)
- Used for Excel file generation with styling

## Usage Instructions

1. **Access the Feature**:
   - Log in to the portal with President or Staff credentials
   - Navigate to the Portal page
   - Click "Merged Dean's List View" in the Tools section

2. **View Data**:
   - Select an academic year from the dropdown
   - The page will automatically reload and display the merged data
   - View statistics about the dataset in the cards above the table

3. **Export to Excel**:
   - Once data is displayed, click the "Export to Excel" button
   - The browser will download a formatted Excel file
   - Open in Excel, Google Sheets, or any spreadsheet application

## Technical Notes

### Performance
- Efficient data merging using Python dictionaries (O(n) complexity)
- Minimal database queries (only 2 queries per year selection)
- Student IDs sorted for consistent display

### Data Handling
- "N/A" displayed for missing semester data
- Handles cases where students appear in only one semester
- Preserves all student information available

### Security
- `@login_required` decorator ensures authentication
- Permission check restricts access to President and Staff roles
- No data modification capability (read-only view)

### Error Handling
- Invalid year selections handled gracefully
- Empty states for no data scenarios
- Messages displayed for any errors

## Future Enhancements (Optional)
- Filter by major
- Search functionality within results
- GPA comparison calculations (average, min, max)
- Semester-by-semester improvement tracking
- PDF export option
- Chart visualizations of GPA trends

## Example Use Cases

1. **Academic Performance Tracking**: Compare individual student performance across semesters
2. **Dean's List Consistency**: Identify students who maintain Dean's List status in both semesters
3. **Report Generation**: Export data for administrative reports or presentations
4. **Data Analysis**: Use exported Excel file for further statistical analysis
5. **Advising**: Reference complete academic year performance for student advising sessions
