import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from main.models import Course
import re
import time
from urllib.parse import urljoin, parse_qs, urlparse


class Command(BaseCommand):
    help = 'Fetch course data from CMU syllabus website'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing courses instead of skipping them',
        )

    def handle(self, *args, **options):
        base_url = "https://cmu.cba.ku.edu.kw/aolapp/syllabus/list/approved/"
        
        try:
            self.stdout.write("Fetching course list from CMU website...")
            
            # Get the main page with course list
            response = requests.get(base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # DEBUG: Save HTML to file for inspection
            with open('debug_cmu_page.html', 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            self.stdout.write("Saved HTML to debug_cmu_page.html for inspection")
            
            # Look for course list items instead of tables
            course_list = soup.find('ul', id='courseList')
            if not course_list:
                self.stdout.write("No courseList found on the page")
                return
                
            course_items = course_list.find_all('li')
            self.stdout.write(f"Found {len(course_items)} course items")
            
            if not course_items:
                self.stdout.write("No course items found in courseList.")
                return
            
            total_courses = len(course_items)
            updated_count = 0
            created_count = 0
            error_count = 0
            
            self.stdout.write(f"Found {total_courses} courses to process...")
            
            for i, item in enumerate(course_items, 1):
                try:
                    course_data = self.extract_course_data(item, base_url)
                    
                    if course_data:
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
                            created_count += 1
                            self.stdout.write(f"Created: {course.course_id}")
                        else:
                            updated_count += 1
                            self.stdout.write(f"Updated: {course.course_id}")
                    
                    # Progress indicator
                    if i % 10 == 0:
                        self.stdout.write(f"Processed {i}/{total_courses} courses...")
                    
                    # Be respectful to the server
                    time.sleep(0.5)
                    
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"Error processing course {i}: {str(e)}")
                    )
                    continue
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Course fetching completed!\n"
                    f"Created: {created_count}\n"
                    f"Updated: {updated_count}\n"
                    f"Errors: {error_count}"
                )
            )
            
            # Clean up invalid courses after fetching
            self.stdout.write("\nCleaning up invalid course IDs...")
            self.cleanup_invalid_courses()
            
        except requests.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to fetch course data: {str(e)}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Unexpected error: {str(e)}")
            )

    def extract_course_data(self, item, base_url):
        """Extract course data from a course list item"""
        try:
            # Extract course code and title from the li element
            course_code_elem = item.find(class_='courseCode')
            course_title_elem = item.find(class_='courseTitle')
            
            if not course_code_elem or not course_title_elem:
                return None
            
            course_id = course_code_elem.get_text(strip=True)
            course_name = course_title_elem.get_text(strip=True)
            
            if not course_id or not course_name:
                return None
            
            # Clean course ID and extract department
            course_id_clean = re.sub(r'[^\w\d\s]', '', course_id).replace(' ', '').upper()
            department = re.match(r'([A-Z]+)', course_id_clean)
            department = department.group(1) if department else None
            
            # Extract credits if available (not visible in current structure, but might be added later)
            credits = None
            
            # Look for download and info links
            syllabus_url = None
            info_url = None
            
            # Find info link first (this is the priority)
            info_link = item.find('a', href=True, string=lambda text: text and 'Info' in text)
            if not info_link:
                # Try finding by URL pattern
                info_link = item.find('a', href=lambda href: href and '/aolapp/syllabus/course/info/' in href)
            
            if info_link:
                info_url = urljoin(base_url, info_link['href'])
                self.stdout.write(f"Processing {course_id_clean}: Found info URL: {info_url}")
                # Try to fetch the most recent syllabus URL from the info page with timeout
                try:
                    syllabus_url = self.get_syllabus_url_from_info_page(info_url)
                    if syllabus_url:
                        self.stdout.write(f"Got syllabus URL from info page: {syllabus_url}")
                    else:
                        self.stdout.write(f"No syllabus URL found on info page for {course_id_clean}")
                except Exception as e:
                    self.stdout.write(f"Error fetching from info page for {course_id_clean}: {str(e)}")
                    syllabus_url = None
            else:
                self.stdout.write(f"No info link found for {course_id_clean}")
            
            # Fallback: Find direct download link if info page doesn't work
            if not syllabus_url:
                download_link = item.find('a', href=True, string=lambda text: text and 'Download' in text)
                if not download_link:
                    # Try finding by icon or class
                    download_link = item.find('a', href=lambda href: href and '/archive/syllabi/' in href)
                if download_link:
                    syllabus_url = urljoin(base_url, download_link['href'])
                    self.stdout.write(f"Using direct download link: {syllabus_url}")
            
            return {
                'course_id': course_id_clean,
                'course_name': course_name,
                'department': department,
                'credits': credits,
                'info_url': info_url,
                'syllabus_url': syllabus_url,
            }
            
        except Exception as e:
            self.stdout.write(f"Error extracting course data: {str(e)}")
            return None

    def get_syllabus_url_from_info_page(self, info_url):
        """Fetch the most recent syllabus download URL from the course info page"""
        try:
            self.stdout.write(f"Fetching info page: {info_url}")
            response = requests.get(info_url, timeout=10)  # Reduced timeout
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for download links in order of preference
            download_candidates = []
            
            # Strategy 1: Look for links with /archive/ in href (syllabus files)
            archive_links = soup.find_all('a', href=lambda href: href and '/archive/' in href)
            for link in archive_links:
                href = link.get('href')
                text = link.get_text(strip=True)
                if any(ext in href.lower() for ext in ['.pdf', '.docx', '.doc']):
                    download_candidates.append((href, text, 'archive'))
            
            # Strategy 2: Look for "Download" buttons or links
            download_links = soup.find_all('a', href=True, string=lambda text: text and 'download' in text.lower())
            for link in download_links:
                href = link.get('href')
                text = link.get_text(strip=True)
                download_candidates.append((href, text, 'download_button'))
            
            # Strategy 3: Look for any PDF/DOC links
            doc_links = soup.find_all('a', href=lambda href: href and any(ext in href.lower() for ext in ['.pdf', '.docx', '.doc']))
            for link in doc_links:
                href = link.get('href')
                text = link.get_text(strip=True)
                download_candidates.append((href, text, 'doc_link'))
            
            if download_candidates:
                # Sort by strategy preference and pick the first one
                strategy_priority = {'archive': 1, 'download_button': 2, 'doc_link': 3}
                download_candidates.sort(key=lambda x: strategy_priority.get(x[2], 999))
                
                best_candidate = download_candidates[0]
                full_url = urljoin(info_url, best_candidate[0])
                self.stdout.write(f"Found syllabus URL: {full_url} (strategy: {best_candidate[2]})")
                return full_url
            
            self.stdout.write(f"No download links found on info page: {info_url}")
            return None
            
        except requests.Timeout:
            self.stdout.write(f"Timeout fetching info page: {info_url}")
            return None
        except requests.RequestException as e:
            self.stdout.write(f"Request error fetching info page {info_url}: {str(e)}")
            return None
        except Exception as e:
            self.stdout.write(f"Error parsing info page {info_url}: {str(e)}")
            return None

    def cleanup_invalid_courses(self):
        """Delete courses with invalid course IDs (not having exactly 3 numbers)"""
        try:
            # Pattern to match valid course IDs: letters followed by exactly 3 digits
            valid_pattern = r'^[A-Z]+\d{3}$'
            
            # Find all courses
            all_courses = Course.objects.all()
            
            invalid_courses = []
            for course in all_courses:
                if not re.match(valid_pattern, course.course_id):
                    invalid_courses.append(course)
            
            if invalid_courses:
                self.stdout.write(f"Found {len(invalid_courses)} courses with invalid course IDs:")
                for course in invalid_courses:
                    self.stdout.write(f"  - {course.course_id}: {course.course_name}")
                
                # Delete invalid courses
                invalid_count = len(invalid_courses)
                Course.objects.filter(id__in=[c.id for c in invalid_courses]).delete()
                
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully deleted {invalid_count} courses with invalid course IDs")
                )
            else:
                self.stdout.write("No courses with invalid course IDs found.")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error during course cleanup: {str(e)}")
            )
