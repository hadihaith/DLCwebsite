#!/usr/bin/env python
import os
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dlcweb.settings')
import django
django.setup()

from main.management.commands.fetch_courses import Command

def test_limited_fetch():
    """Test the fetch_courses command with only the first 3 courses"""
    cmd = Command()
    
    # Override the handle method to limit to 3 courses
    import requests
    from bs4 import BeautifulSoup
    
    base_url = "https://cmu.cba.ku.edu.kw/aolapp/syllabus/list/approved/"
    
    try:
        print("Fetching course list from CMU website...")
        
        # Get the main page with course list
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for course list items
        course_list = soup.find('ul', id='courseList')
        if not course_list:
            print("No courseList found on the page")
            return
            
        course_items = course_list.find_all('li')
        print(f"Found {len(course_items)} course items total")
        
        # Limit to first 3 courses for testing
        test_items = course_items[:3]
        print(f"Testing with first {len(test_items)} courses...")
        
        for i, item in enumerate(test_items, 1):
            try:
                print(f"\n--- Processing course {i} ---")
                course_data = cmd.extract_course_data(item, base_url)
                
                if course_data:
                    print(f"Course ID: {course_data['course_id']}")
                    print(f"Course Name: {course_data['course_name']}")
                    print(f"Department: {course_data['department']}")
                    print(f"Info URL: {course_data.get('info_url', 'None')}")
                    print(f"Syllabus URL: {course_data.get('syllabus_url', 'None')}")
                    
                    # Save to database
                    from main.models import Course
                    course, created = Course.objects.update_or_create(
                        course_id=course_data['course_id'],
                        defaults={
                            'course_name': course_data['course_name'],
                            'syllabus_url': course_data.get('syllabus_url'),
                            'info_url': course_data.get('info_url'),
                            'department': course_data.get('department'),
                            'credits': course_data.get('credits'),
                            'is_active': True,
                        }
                    )
                    
                    if created:
                        print(f"✓ Created course: {course.course_id}")
                    else:
                        print(f"✓ Updated course: {course.course_id}")
                else:
                    print("Failed to extract course data")
                    
            except Exception as e:
                print(f"Error processing course {i}: {str(e)}")
                continue
        
        print(f"\nTest completed!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_limited_fetch()