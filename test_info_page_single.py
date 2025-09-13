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

def test_single_course():
    """Test the fetch_courses command with only one course"""
    cmd = Command()
    
    # Test with a specific course info URL
    info_url = "https://cmu.cba.ku.edu.kw/aolapp/syllabus/course/info/1011/201/"
    print(f"Testing info page fetching for: {info_url}")
    
    try:
        syllabus_url = cmd.get_syllabus_url_from_info_page(info_url)
        print(f"Result: {syllabus_url}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_single_course()