
from .models import Application, User, DeanListStudent, DeanList, Thread, Reply, ThreadSettings, majors
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.base import ContentFile
from datetime import datetime, timedelta
from .utils import process_dean_list_excel
from user_agents import parse
from django.contrib import messages
from django.db.models import Q
import random
from decimal import Decimal
import os
import re
from .forms import EventForm
import requests
from django.http import HttpResponse, HttpResponseBadRequest
from urllib.parse import urlparse, quote
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404


def cleanup_invalid_course_ids():
    """
    Utility function to delete courses with invalid course IDs.
    Valid course IDs should have letters followed by exactly 3 digits (e.g., ACC201, FIN305).
    Invalid examples: ACC0, MGTMKT1011220, ACC, FIN12, etc.
    """
    try:
        from .models import Course
        
        # Pattern to match valid course IDs: letters followed by exactly 3 digits
        valid_pattern = r'^[A-Z]+\d{3}$'
        
        # Find all courses with invalid IDs
        all_courses = Course.objects.all()
        invalid_courses = []
        
        for course in all_courses:
            if not re.match(valid_pattern, course.course_id):
                invalid_courses.append(course)
        
        if invalid_courses:
            print(f"Found {len(invalid_courses)} courses with invalid course IDs:")
            for course in invalid_courses:
                print(f"  - {course.course_id}: {course.course_name}")
            
            # Delete invalid courses
            invalid_count = len(invalid_courses)
            Course.objects.filter(id__in=[c.id for c in invalid_courses]).delete()
            
            print(f"Successfully deleted {invalid_count} courses with invalid course IDs")
            return invalid_count
        else:
            print("No courses with invalid course IDs found.")
            return 0
            
    except Exception as e:
        print(f"Error during course cleanup: {str(e)}")
        return -1
from django.db.models import Q

def home(request):
    return render(request, 'frontend/index.html')

def resources(request):
    """Resources page with three main sections"""
    return render(request, 'frontend/resources.html')

def student_guide(request):
    """Student guide page with downloadable guides by year"""
    selected_year = request.GET.get('year', '2023')  # Default to 2023
    
    # Student guide data organized by year
    student_guides = {
        '2023': [
            {
                'title': 'Information Systems Management (نظم المعلومات الادارية)',
                'description': 'Study guide for Information Systems Management major 2023',
                'download_url': 'https://drive.google.com/file/d/1lakt3HdGxPv4cVSxvgOEMg6D25i2L3Zl/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1lakt3HdGxPv4cVSxvgOEMg6D25i2L3Zl/preview',
                'category': 'Information Systems',
                'size': 'PDF'
            },
            {
                'title': 'Public Administration (الادارة العامه)',
                'description': 'Study guide for Public Administration major 2023',
                'download_url': 'https://drive.google.com/file/d/1I675DMORINOxrUENdvo8FvKJNO2na5OS/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1I675DMORINOxrUENdvo8FvKJNO2na5OS/preview',
                'category': 'Public Administration',
                'size': 'PDF'
            },
            {
                'title': 'Economics (الاقتصاد)',
                'description': 'Study guide for Economics major 2023',
                'download_url': 'https://drive.google.com/file/d/1x19PYd7PMwMOMJIpb4kCfjucRHGzmQ14/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1x19PYd7PMwMOMJIpb4kCfjucRHGzmQ14/preview',
                'category': 'Economics',
                'size': 'PDF'
            },
            {
                'title': 'Marketing (التسويق)',
                'description': 'Study guide for Marketing major 2023',
                'download_url': 'https://drive.google.com/file/d/1iTukxKgAfGcepcYi4yHpIrFEdjGOuFZn/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1iTukxKgAfGcepcYi4yHpIrFEdjGOuFZn/preview',
                'category': 'Marketing',
                'size': 'PDF'
            },
            {
                'title': 'Management (الادارة)',
                'description': 'Study guide for Management major 2023',
                'download_url': 'https://drive.google.com/file/d/198SS0XmI0VsJUf_2sisrCkNfEuKFeGw_/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/198SS0XmI0VsJUf_2sisrCkNfEuKFeGw_/preview',
                'category': 'Management',
                'size': 'PDF'
            },
            {
                'title': 'Accounting (المحاسبة)',
                'description': 'Study guide for Accounting major 2023',
                'download_url': 'https://drive.google.com/file/d/1VynuiD99Oo0Hm51RE8Gwnjj7MYVxeq0w/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1VynuiD99Oo0Hm51RE8Gwnjj7MYVxeq0w/preview',
                'category': 'Accounting',
                'size': 'PDF'
            },
            {
                'title': 'Operations Management & Supply Chain (ادارة العمليات وسلسلة الامدادات)',
                'description': 'Study guide for Operations Management & Supply Chain major 2023',
                'download_url': 'https://drive.google.com/file/d/1DtKEq9C0J3Gv2KNbQPSaZYLzsFpYAxCG/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1DtKEq9C0J3Gv2KNbQPSaZYLzsFpYAxCG/preview',
                'category': 'Operations Management',
                'size': 'PDF'
            },
            {
                'title': 'Finance & Financial Institutions (التمويل و المنشآت الماليه)',
                'description': 'Study guide for Finance & Financial Institutions major 2023',
                'download_url': 'https://drive.google.com/file/d/1ohcceBnBC48cHOfA-YLMRETWC7sVpRqb/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1ohcceBnBC48cHOfA-YLMRETWC7sVpRqb/preview',
                'category': 'Finance',
                'size': 'PDF'
            }
        ],
        '2024': [
            {
                'title': 'Management (الادارة)',
                'description': 'Study guide for Management major 2024',
                'download_url': 'https://drive.google.com/file/d/1OX-YpB0ZaX1uH8NoKCCGTOHR7EErXFg2/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1OX-YpB0ZaX1uH8NoKCCGTOHR7EErXFg2/preview',
                'category': 'Management',
                'size': 'PDF'
            },
            {
                'title': 'Public Administration (الادارة العامه)',
                'description': 'Study guide for Public Administration major 2024',
                'download_url': 'https://drive.google.com/file/d/11QoBKNF3iJz25rRKExSaGFDpDQmBL5Pw/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/11QoBKNF3iJz25rRKExSaGFDpDQmBL5Pw/preview',
                'category': 'Public Administration',
                'size': 'PDF'
            },
            {
                'title': 'Accounting (المحاسبة)',
                'description': 'Study guide for Accounting major 2024',
                'download_url': 'https://drive.google.com/file/d/1m34Rpp1cDsVgLPqDk1h9ys66ChQ3WxYx/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1m34Rpp1cDsVgLPqDk1h9ys66ChQ3WxYx/preview',
                'category': 'Accounting',
                'size': 'PDF'
            },
            {
                'title': 'Economics (الاقتصاد)',
                'description': 'Study guide for Economics major 2024',
                'download_url': 'https://drive.google.com/file/d/1ydN5ZCdIA8XXwEZDC-_sikMZYU2PcFr8/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1ydN5ZCdIA8XXwEZDC-_sikMZYU2PcFr8/preview',
                'category': 'Economics',
                'size': 'PDF'
            },
            {
                'title': 'Marketing (التسويق)',
                'description': 'Study guide for Marketing major 2024',
                'download_url': 'https://drive.google.com/file/d/1fj9E_6rbGzgfFnRBdhuVx29aLdzBz5ba/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1fj9E_6rbGzgfFnRBdhuVx29aLdzBz5ba/preview',
                'category': 'Marketing',
                'size': 'PDF'
            },
            {
                'title': 'Operations Management & Supply Chain (ادارة العمليات وسلسلة الامدادات)',
                'description': 'Study guide for Operations Management & Supply Chain major 2024',
                'download_url': 'https://drive.google.com/file/d/1P_Xad-CX_E1ztf9EkZ_mI2la_OXyOic5/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1P_Xad-CX_E1ztf9EkZ_mI2la_OXyOic5/preview',
                'category': 'Operations Management',
                'size': 'PDF'
            },
            {
                'title': 'Finance & Financial Institutions (التمويل والمنشآت المالية)',
                'description': 'Study guide for Finance & Financial Institutions major 2024',
                'download_url': 'https://drive.google.com/file/d/1wtArpekA6YVFJpCiMurdUgk-q1Tv0oqD/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1wtArpekA6YVFJpCiMurdUgk-q1Tv0oqD/preview',
                'category': 'Finance',
                'size': 'PDF'
            }
        ],
        '2025': [
            {
                'title': 'Public Administration (الادارة العامه)',
                'description': 'Study guide for Public Administration major 2025',
                'download_url': 'https://drive.google.com/file/d/1W_D0FPwy9a08xtg5_amD__qBAusxjcZD/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1W_D0FPwy9a08xtg5_amD__qBAusxjcZD/preview',
                'category': 'Public Administration',
                'size': 'PDF'
            },
            {
                'title': 'Economics (الاقتصاد)',
                'description': 'Study guide for Economics major 2025',
                'download_url': 'https://drive.google.com/file/d/1uCxk6tg1DpTBhzWG4Dej5vGbo__SBmPZ/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1uCxk6tg1DpTBhzWG4Dej5vGbo__SBmPZ/preview',
                'category': 'Economics',
                'size': 'PDF'
            },
            {
                'title': 'Marketing (التسويق)',
                'description': 'Study guide for Marketing major 2025',
                'download_url': 'https://drive.google.com/file/d/1_emotOjnlXXxMMOCZXkuniinLct2SQJs/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1_emotOjnlXXxMMOCZXkuniinLct2SQJs/preview',
                'category': 'Marketing',
                'size': 'PDF'
            },
            {
                'title': 'Operations Management & Supply Chain (ادارة العمليات وسلسلة الامدادات)',
                'description': 'Study guide for Operations Management & Supply Chain major 2025',
                'download_url': 'https://drive.google.com/file/d/1u8e3ovjp-8KXM1m9cwER--U0WW2iGICj/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1u8e3ovjp-8KXM1m9cwER--U0WW2iGICj/preview',
                'category': 'Operations Management',
                'size': 'PDF'
            },
            {
                'title': 'Information Systems Management (نظم المعلومات)',
                'description': 'Study guide for Information Systems Management major 2025',
                'download_url': 'https://drive.google.com/file/d/1KtUsdcfd5kHnDvVrvj3S54sG_DRiekYu/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1KtUsdcfd5kHnDvVrvj3S54sG_DRiekYu/preview',
                'category': 'Information Systems',
                'size': 'PDF'
            },
            {
                'title': 'Finance & Financial Institutions (التمويل والمنشآت المالية)',
                'description': 'Study guide for Finance & Financial Institutions major 2025',
                'download_url': 'https://drive.google.com/file/d/1_UmQ2BwcrABtgYOIG-qVKmJxD0S099yA/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1_UmQ2BwcrABtgYOIG-qVKmJxD0S099yA/preview',
                'category': 'Finance',
                'size': 'PDF'
            },
            {
                'title': 'Accounting (المحاسبة)',
                'description': 'Study guide for Accounting major 2025',
                'download_url': 'https://drive.google.com/file/d/1tqPPjTgJyxk_pyhx5SWHfwWTNnuSsf0g/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1tqPPjTgJyxk_pyhx5SWHfwWTNnuSsf0g/preview',
                'category': 'Accounting',
                'size': 'PDF'
            },
            {
                'title': 'Management (الادارة)',
                'description': 'Study guide for Management major 2025',
                'download_url': 'https://drive.google.com/file/d/1iiJQGxDt609ZvtdyVS7qeRgFYQX9smfq/view?usp=drive_link',
                'view_url': 'https://drive.google.com/file/d/1iiJQGxDt609ZvtdyVS7qeRgFYQX9smfq/preview',
                'category': 'Management',
                'size': 'PDF'
            }
        ]
    }
    
    # Get guides for selected year
    guides = student_guides.get(selected_year, [])
    
    # Group guides by category
    guides_by_category = {}
    for guide in guides:
        category = guide['category']
        if category not in guides_by_category:
            guides_by_category[category] = []
        guides_by_category[category].append(guide)
    
    context = {
        'selected_year': selected_year,
        'available_years': ['2023', '2024', '2025'],
        'guides': guides,
        'guides_by_category': guides_by_category,
        'total_guides': len(guides)
    }
    
    return render(request, 'frontend/student_guide.html', context)

def course_descriptions(request):
    """Course descriptions and syllabuses page"""
    try:
        from .models import Course
        from django.core.paginator import Paginator
        
        # Get all courses ordered by course ID
        courses = Course.objects.filter(is_active=True).order_by('course_id')
        
        # Filter by department if requested
        department = request.GET.get('department')
        if department:
            courses = courses.filter(department=department)
        
        # Search functionality
        search_query = request.GET.get('search')
        if search_query:
            courses = courses.filter(
                Q(course_id__icontains=search_query) | 
                Q(course_name__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(courses, 25)  # Show 25 courses per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get unique departments for filter dropdown
        departments_queryset = Course.objects.filter(is_active=True).values_list('department', flat=True)
        departments = list(set([dept for dept in departments_queryset if dept]))  # Use set() to ensure uniqueness
        
        context = {
            'page_obj': page_obj,
            'courses': page_obj,
            'departments': sorted(departments),
            'current_department': department,
            'search_query': search_query,
            'total_courses': courses.count(),
        }
        
    except Exception as e:
        # Handle case where Course model doesn't exist or database issues
        context = {
            'page_obj': None,
            'courses': [],
            'departments': [],
            'current_department': None,
            'search_query': request.GET.get('search'),
            'total_courses': 0,
            'error_message': 'Course data is not available. Please contact the administrator.'
        }
    
    return render(request, 'frontend/course_descriptions.html', context)

def apply(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        student_id = request.POST.get('student_id')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        GPA = request.POST.get('GPA')
        passed_credits = request.POST.get('passed_credits')
        major = request.POST.get('major')
        anything_else = request.POST.get('anything_else')
        applications = Application.objects.all()
        if applications.filter(student_id=student_id).exists():
            return render(request, 'frontend/apply.html', {'error': 'You have already submitted an application. Please wait for a response before submitting another.'})
        application = Application(
            name=name,
            student_id=student_id,
            phone=phone,
            email=email,
            passed_credits=passed_credits,
            GPA=GPA,
            major=major,
            anything_else=anything_else
        )
        
        application.save()
        return render(request, 'frontend/success.html', {'application': application})
    return render(request, 'frontend/apply.html')


def members(request):
    members = User.objects.filter(is_member=True)
    # order members by role, president first, vice president second, etc.
    new_order = ['PRESIDENT', 'VICE_PRESIDENT', 'SECRETARY', 'TREASURER', 'MEMBER']
    members = sorted(members, key=lambda x: new_order.index(x.role) if x.role in new_order else 100)
    return render(request, 'frontend/members.html', {'members': members})

@login_required
def portal(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    # Device detection - block mobile and tablet devices
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    
    if user_agent.is_mobile or user_agent.is_tablet:
        # Render a "desktop only" message page
        return render(request, 'frontend/desktop_only.html', {
            'device_type': 'mobile device' if user_agent.is_mobile else 'tablet'
        })
    
    # user_count is now automatically available via context processor
    # include events for portal users
    try:
        from .models import Event
        events = Event.objects.all().order_by('-start_date')
    except Exception:
        events = []

    return render(request, 'frontend/portal.html', {'user': request.user, 'events': events})


@login_required
def refresh_courses(request):
    """Admin view to refresh course data from CMU website"""
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    # Check if user has permission (only president and staff can access)
    if not (request.user.role == 'PRESIDENT' or request.user.is_staff):
        return HttpResponseForbidden("Access denied. President or staff access required.")
    
    if request.method == 'POST':
        try:
            from django.core.management import call_command
            from .models import Course
            import io
            from contextlib import redirect_stdout
            
            # Capture the output of the management command
            output = io.StringIO()
            
            # Delete all existing courses
            deleted_count = Course.objects.count()
            Course.objects.all().delete()
            
            # Run the fetch_courses command
            with redirect_stdout(output):
                call_command('fetch_courses')
            
            command_output = output.getvalue()
            
            # Get the new course count
            new_count = Course.objects.count()
            
            # Run additional cleanup to ensure no invalid course IDs remain
            cleanup_count = cleanup_invalid_course_ids()
            final_count = Course.objects.count()
            
            success_message = f"Course refresh completed successfully!\nDeleted: {deleted_count} old courses\nFetched: {new_count} new courses"
            
            if cleanup_count > 0:
                success_message += f"\nCleaned up: {cleanup_count} invalid course IDs\nFinal count: {final_count} valid courses"
            
            messages.success(request, success_message)
            
            # Log the refresh action
            print(f"Course refresh by {request.user.username}: {deleted_count} deleted, {new_count} fetched, {cleanup_count} cleaned up")
            
        except Exception as e:
            messages.error(
                request,
                f"Error refreshing courses: {str(e)}"
            )
    
    # Get current course statistics
    try:
        from .models import Course
        total_courses = Course.objects.count()
        # Get unique departments properly using set() to avoid duplicates
        departments_queryset = Course.objects.values_list('department', flat=True)
        unique_departments = sorted(set([dept for dept in departments_queryset if dept]))
        active_courses = Course.objects.filter(is_active=True).count()
        courses_with_syllabus = Course.objects.filter(syllabus_url__isnull=False).count()
    except Exception as e:
        # Handle case where Course model doesn't exist or database table hasn't been created
        total_courses = 0
        unique_departments = []
        active_courses = 0
        courses_with_syllabus = 0
    
    context = {
        'total_courses': total_courses,
        'departments': unique_departments,
        'active_courses': active_courses,
        'courses_with_syllabus': courses_with_syllabus,
        'user': request.user,
    }
    
    return render(request, 'frontend/refresh_courses.html', context)


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("portal"))
        else:
            return render(request, "frontend/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("portal"))
        return render(request, "frontend/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))



@login_required
def add_member(request):
    """
    Add new member functionality - accessible to all users but only functional for authorized roles
    Supports both single member and bulk member creation
    """
    # Device detection - block mobile and tablet devices
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    
    if user_agent.is_mobile or user_agent.is_tablet:
        return render(request, 'frontend/desktop_only.html', {
            'device_type': 'mobile device' if user_agent.is_mobile else 'tablet'
        })
    
    # Check if user has permission to add members
    allowed_roles = ['PRESIDENT', 'VICE_PRESIDENT', 'MANAGER']
    can_add_member = request.user.is_superuser or request.user.is_staff or request.user.role in allowed_roles
    
    message = None
    error_message = None
    bulk_results = None
    
    if request.method == "POST" and can_add_member:
        # Check if this is a bulk creation request
        bulk_data = request.POST.get("bulk_data", "").strip()
        
        if bulk_data:
            # Handle bulk member creation
            bulk_results = process_bulk_member_creation(bulk_data)
            if bulk_results['success_count'] > 0:
                message = f"Successfully created {bulk_results['success_count']} member(s)."
            if bulk_results['error_count'] > 0:
                error_message = f"Failed to create {bulk_results['error_count']} member(s). See details below."
        else:
            # Handle single member creation (existing logic)
            username = request.POST.get("username", "").strip()
            password = request.POST.get("password", "").strip()
            first_name = request.POST.get("first_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            role = request.POST.get("role", "MEMBER")
            is_member = request.POST.get("is_member") == "on"
            
            # Validation
            if not all([username, password, first_name, last_name]):
                error_message = "All fields are required."
            elif len(password) < 6:
                error_message = "Password must be at least 6 characters long."
            elif User.objects.filter(username=username).exists():
                error_message = "Username already exists. Please choose a different username."
            else:
                try:
                    # Create new user with hardcoded email
                    user = User.objects.create_user(
                        username=username,
                        email="sss@sss.com",
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    user.role = role
                    user.is_member = is_member
                    user.save()
                    
                    message = f"Member '{first_name} {last_name}' has been successfully created with username '{username}'."
                    
                except IntegrityError:
                    error_message = "An error occurred while creating the user. Username might already exist."
                except Exception as e:
                    error_message = f"An unexpected error occurred: {str(e)}"
    
    elif request.method == "POST" and not can_add_member:
        error_message = "You don't have permission to add new members."
    
    # Get role choices for the dropdown
    role_choices = [
        ('PRESIDENT', 'President'),
        ('VICE_PRESIDENT', 'Vice President'),
        ('SECRETARY', 'Secretary'),
        ('TREASURER', 'Treasurer'),
        ('MANAGER', 'Manager'),
        ('MEMBER', 'Member'),
    ]
    
    context = {
        'can_add_member': can_add_member,
        'message': message,
        'error_message': error_message,
        'bulk_results': bulk_results,
        'role_choices': role_choices,
        'user': request.user,
    }
    
    return render(request, 'frontend/add_member.html', context)


def process_bulk_member_creation(bulk_data):
    """
    Process bulk member creation from multiline string format:
    username,password,First_name Last_name
    
    Example:
    alaadlc,mar7badawli,Alaa El Haj
    mai.Abd,mis2025,Maida Abdullah
    
    Returns dict with success_count, error_count, successes list, and errors list
    """
    results = {
        'success_count': 0,
        'error_count': 0,
        'successes': [],
        'errors': []
    }
    
    lines = bulk_data.strip().split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        
        parts = [p.strip() for p in line.split(',')]
        
        if len(parts) != 3:
            results['errors'].append({
                'line': line_num,
                'data': line,
                'error': f'Invalid format. Expected 3 comma-separated values, got {len(parts)}.'
            })
            results['error_count'] += 1
            continue
        
        username, password, full_name = parts
        
        # Split full name into first and last name
        name_parts = full_name.split()
        if len(name_parts) < 2:
            results['errors'].append({
                'line': line_num,
                'data': line,
                'error': 'Full name must contain at least first and last name.'
            })
            results['error_count'] += 1
            continue
        
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:])  # Everything after first name is last name
        
        # Validate
        if not username or not password or not first_name or not last_name:
            results['errors'].append({
                'line': line_num,
                'data': line,
                'error': 'Username, password, and full name cannot be empty.'
            })
            results['error_count'] += 1
            continue
        
        if len(password) < 6:
            results['errors'].append({
                'line': line_num,
                'data': line,
                'error': 'Password must be at least 6 characters long.'
            })
            results['error_count'] += 1
            continue
        
        if User.objects.filter(username=username).exists():
            results['errors'].append({
                'line': line_num,
                'data': line,
                'error': f'Username "{username}" already exists.'
            })
            results['error_count'] += 1
            continue
        
        # Create the user
        try:
            user = User.objects.create_user(
                username=username,
                email="sss@sss.com",
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            user.role = 'MEMBER'
            user.is_member = True
            user.save()
            
            results['successes'].append({
                'line': line_num,
                'username': username,
                'name': f'{first_name} {last_name}'
            })
            results['success_count'] += 1
            
        except IntegrityError:
            results['errors'].append({
                'line': line_num,
                'data': line,
                'error': f'Database error: Username "{username}" might already exist.'
            })
            results['error_count'] += 1
        except Exception as e:
            results['errors'].append({
                'line': line_num,
                'data': line,
                'error': f'Unexpected error: {str(e)}'
            })
            results['error_count'] += 1
    
    return results


@login_required
def manage_members(request):
    """
    Manage members functionality - accessible only to president and staff
    Allows deleting members and changing their roles
    """
    # Device detection - block mobile and tablet devices
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    
    if user_agent.is_mobile or user_agent.is_tablet:
        return render(request, 'frontend/desktop_only.html', {
            'device_type': 'mobile device' if user_agent.is_mobile else 'tablet'
        })
    
    # Check if user has permission to manage members
    allowed_roles = ['PRESIDENT']
    can_manage = request.user.is_superuser or request.user.is_staff or request.user.role in allowed_roles
    
    if not can_manage:
        return render(request, 'frontend/access_denied.html', {
            'message': 'Only President and Staff can manage members.',
            'required_roles': ['President', 'Staff']
        })
    
    # Get all users ordered by role hierarchy
    role_order = ['PRESIDENT', 'VICE_PRESIDENT', 'SECRETARY', 'TREASURER', 'MANAGER', 'MEMBER']
    all_users = User.objects.all().order_by('is_staff', 'is_superuser')
    
    # Sort users by role hierarchy
    users = sorted(all_users, key=lambda x: (
        0 if x.is_superuser else 1,
        0 if x.is_staff else 1,
        role_order.index(x.role) if x.role in role_order else 100,
        x.first_name.lower() if x.first_name else x.username.lower()
    ))
    
    # Get role choices for the dropdown
    role_choices = [
        ('PRESIDENT', 'President'),
        ('VICE_PRESIDENT', 'Vice President'),
        ('SECRETARY', 'Secretary'),
        ('TREASURER', 'Treasurer'),
        ('MANAGER', 'Manager'),
        ('MEMBER', 'Member'),
    ]
    
    # Calculate statistics
    total_users = len(users)
    active_members = len([u for u in users if u.is_member])
    staff_users = len([u for u in users if u.is_staff or u.is_superuser])
    
    context = {
        'users': users,
        'role_choices': role_choices,
        'total_users': total_users,
        'active_members': active_members,
        'staff_users': staff_users,
        'current_user': request.user,
    }
    
    return render(request, 'frontend/manage_members.html', context)


@login_required
@require_POST
def update_member_role(request, user_id):
    """
    Update a member's role - only for president and staff
    """
    # Check if user has permission
    allowed_roles = ['PRESIDENT']
    if not (request.user.is_superuser or request.user.is_staff or request.user.role in allowed_roles):
        return JsonResponse({'success': False, 'message': 'Insufficient permissions'})
    
    try:
        member = User.objects.get(id=user_id)
        new_role = request.POST.get('role')
        new_is_member = request.POST.get('is_member') == 'true'
        
        # Prevent users from modifying superusers unless they are superuser themselves
        if member.is_superuser and not request.user.is_superuser:
            return JsonResponse({'success': False, 'message': 'Cannot modify superuser accounts'})
        
        # Prevent users from removing the last president (unless they are superuser)
        if member.role == 'PRESIDENT' and new_role != 'PRESIDENT' and not request.user.is_superuser:
            president_count = User.objects.filter(role='PRESIDENT').count()
            if president_count <= 1:
                return JsonResponse({'success': False, 'message': 'Cannot remove the last president'})
        
        # Update the member
        member.role = new_role
        member.is_member = new_is_member
        member.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully updated {member.first_name} {member.last_name}\'s role to {new_role}'
        })
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_POST
def delete_member(request, user_id):
    """
    Delete a member - only for president and staff
    """
    # Check if user has permission
    allowed_roles = ['PRESIDENT']
    if not (request.user.is_superuser or request.user.is_staff or request.user.role in allowed_roles):
        return JsonResponse({'success': False, 'message': 'Insufficient permissions'})
    
    try:
        member = User.objects.get(id=user_id)
        
        # Prevent deletion of self
        if member.id == request.user.id:
            return JsonResponse({'success': False, 'message': 'Cannot delete your own account'})
        
        # Prevent deletion of superusers unless the current user is superuser
        if member.is_superuser and not request.user.is_superuser:
            return JsonResponse({'success': False, 'message': 'Cannot delete superuser accounts'})
        
        # Prevent deletion of the last president (unless current user is superuser)
        if member.role == 'PRESIDENT' and not request.user.is_superuser:
            president_count = User.objects.filter(role='PRESIDENT').count()
            if president_count <= 1:
                return JsonResponse({'success': False, 'message': 'Cannot delete the last president'})
        
        member_name = f"{member.first_name} {member.last_name}"
        member.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully deleted {member_name}'
        })
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@user_passes_test(lambda u: u.is_staff)
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = "sss@sss.com"
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]


        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "frontend/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
            user.save()
        except IntegrityError:
            return render(request, "frontend/register.html", {
                "message": "Username is already previously taken."
            })
        return HttpResponseRedirect(reverse("home"))
    else:
        if request.user.is_staff:
            return render(request, "frontend/register.html")



@login_required
def newdl(request):
    # Device detection - block mobile and tablet devices
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    
    if user_agent.is_mobile or user_agent.is_tablet:
        # Render a "desktop only" message page
        return render(request, 'frontend/desktop_only.html', {
            'device_type': 'mobile device' if user_agent.is_mobile else 'tablet'
        })
    
    if request.method == 'POST':
        semester = request.POST.get('semester')
        year = request.POST.get('year')
        excel_file = request.FILES.get('excel_file')   
        if not semester or not year or not excel_file:
            context = {
                'message': 'All fields are required.',
                'years': range(2007, 2046) 
            }
            return render(request, 'frontend/newdl.html', context)
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            context = {
                'message': 'Please upload a valid Excel file (.xlsx or .xls).',
                'years': range(2007, 2046)
            }
            return render(request, 'frontend/newdl.html', context)      
        try:
            file_extension = os.path.splitext(excel_file.name)[1]  
            new_filename = f"{semester}{year}dean list{file_extension}"        
            file_content = excel_file.read()
            renamed_file = ContentFile(file_content, name=new_filename)
            dean_list = DeanList.objects.create(
                semester=semester,
                year=int(year),
                excel_file=renamed_file
            )
            dean_list.save()
            excel_file.seek(0)
            df, header_row, students_saved = process_dean_list_excel(excel_file, semester, year)
            print(f"Processing completed: header at row {header_row}, {students_saved} students saved")

            return render(request, 'frontend/newdl.html', {
                'message': f'Dean\'s list created successfully. {students_saved} students imported.',
                'years': range(2007, 2046)
            }) 
            
        except Exception as e:
            context = {
                'message': f'Error creating dean\'s list: {str(e)}',
                'years': range(2007, 2046)
            }
            return render(request, 'frontend/newdl.html', context)

    context = {
        'years': range(2007, 2046)
    }
    return render(request, 'frontend/newdl.html', context)


def deanslist(request):
    """
    Display dean's list students filtered by semester and year.
    Group by major and order by GPA (descending) within each major.
    """
    # Get available semesters and years from the database
    available_lists = DeanList.objects.values('semester', 'year').distinct().order_by('-year', 'semester')
    
    # Initialize variables
    students_by_major = {}
    selected_semester = request.GET.get('semester', '')
    selected_year = request.GET.get('year', '')
    selected_major = request.GET.get('major', '')
    available_majors = []
    
    # If semester and year are provided, get the students
    if selected_semester and selected_year:
        try:
            year_int = int(selected_year)
            students = DeanListStudent.objects.filter(
                semester=selected_semester,
                year=year_int
            ).order_by('student_major', '-gpa', '-passed_credits', 'student_name')
            
            # Get unique majors for this specific semester/year
            available_majors = students.values_list('student_major', flat=True).distinct().order_by('student_major')
            available_majors = [major for major in available_majors if major and major.strip()]  # Remove empty majors
            
            # Group students by major
            for student in students:
                major = student.student_major
                if not major or not major.strip():
                    major = 'Unknown'
                else:
                    major = major.strip()
                    
                if major not in students_by_major:
                    students_by_major[major] = []
                students_by_major[major].append(student)
            
            # If a specific major is selected, filter to show only that major
            if selected_major and selected_major.strip():
                print(f"DEBUG: Selected major: '{selected_major}'")
                print(f"DEBUG: Available majors in students_by_major: {list(students_by_major.keys())}")
                if selected_major in students_by_major:
                    students_by_major = {selected_major: students_by_major[selected_major]}
                    print(f"DEBUG: Filtered to show only {selected_major}: {len(students_by_major[selected_major])} students")
                else:
                    # Selected major not found for this semester/year
                    students_by_major = {}
                    print(f"DEBUG: Selected major '{selected_major}' not found for {selected_semester} {selected_year}")
                    
        except ValueError:
            # Invalid year format
            students_by_major = {}
            available_majors = []
    else:
        # Get all unique majors from all records for the dropdown when no semester/year selected
        all_majors = DeanListStudent.objects.values_list('student_major', flat=True).distinct().order_by('student_major')
        available_majors = [major for major in all_majors if major and major.strip()]
    
    # Get available years from the database
    available_years = DeanListStudent.objects.values_list('year', flat=True).distinct().order_by('year')
    
    context = {
        'available_lists': available_lists,
        'all_majors': sorted(available_majors),
        'students_by_major': students_by_major,
        'selected_semester': selected_semester,
        'selected_year': selected_year,
        'selected_major': selected_major,
        'years': sorted(available_years),
        'total_students': sum(len(students) for students in students_by_major.values()),
    }
    
    return render(request, 'frontend/deanslist.html', context)


@login_required
def student_search(request):
    """
    Search for students by ID or name and display their dean's list rankings
    """
    # Device detection - block mobile and tablet devices
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    
    if user_agent.is_mobile or user_agent.is_tablet:
        return render(request, 'frontend/desktop_only.html', {
            'device_type': 'mobile device' if user_agent.is_mobile else 'tablet'
        })
    
    search_results = []
    search_query = ""
    search_type = ""
    multiple_matches = False
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id', '').strip()
        student_name = request.POST.get('student_name', '').strip()
        
        if student_id:
            # Search by student ID (exact match)
            search_query = student_id
            search_type = "ID"
            students = DeanListStudent.objects.filter(student_id=student_id).order_by('year', 'semester')
            
            if students.exists():
                search_results = calculate_student_rankings(students, request.user)
            
        elif student_name:
            # Search by name (substring matching with better Arabic support)
            search_query = student_name
            search_type = "name"
            
            # Split the search query into individual words for better matching
            search_words = [word.strip() for word in student_name.split() if word.strip()]
            
            if search_words:
                # Build a query that matches all words in any order within the name
                query = Q()
                for word in search_words:
                    query &= Q(student_name__icontains=word)
                
                students = DeanListStudent.objects.filter(query).order_by('student_name', 'year', 'semester')
            else:
                students = DeanListStudent.objects.none()
            
            if students.exists():
                # Group by student name to handle multiple matches
                students_by_name = {}
                for student in students:
                    name = student.student_name
                    if name not in students_by_name:
                        students_by_name[name] = []
                    students_by_name[name].append(student)
                
                # If multiple different names match, show selection
                if len(students_by_name) > 1:
                    multiple_matches = True
                    search_results = [
                        {
                            'student_name': name,
                            'student_id': students_list[0].student_id,
                            'appearances': len(students_list),
                            'years': sorted(list(set(f"{s.semester} {s.year}" for s in students_list)))
                        }
                        for name, students_list in students_by_name.items()
                    ]
                else:
                    # Single name match, show full rankings
                    all_students = list(students)
                    search_results = calculate_student_rankings(all_students, request.user)
    
    context = {
        'search_results': search_results,
        'search_query': search_query,
        'search_type': search_type,
        'multiple_matches': multiple_matches,
    }
    
    return render(request, 'frontend/student_search.html', context)


def calculate_student_rankings(students, user):
    """
    Calculate rankings for a student across different semesters/years
    """
    results = []
    
    # Group by semester and year
    by_semester_year = {}
    for student in students:
        key = f"{student.semester}_{student.year}"
        if key not in by_semester_year:
            by_semester_year[key] = []
        by_semester_year[key].append(student)
    
    # For each semester/year, calculate the student's ranking
    for semester_year_key, student_list in by_semester_year.items():
        student = student_list[0]  # Should be only one per semester/year
        semester = student.semester
        year = student.year
        
        # Get all students for this semester/year, ordered by GPA descending
        all_students_in_semester = DeanListStudent.objects.filter(
            semester=semester,
            year=year
        ).order_by('-gpa', 'student_name')
        
        # Find the overall ranking (1-based)
        overall_ranking = 1
        for idx, s in enumerate(all_students_in_semester):
            if s.student_id == student.student_id:
                overall_ranking = idx + 1
                break
        
        total_students = all_students_in_semester.count()
        
        # Calculate ranking within major
        students_in_major = DeanListStudent.objects.filter(
            semester=semester,
            year=year,
            student_major=student.student_major
        ).order_by('-gpa', 'student_name')
        
        # Find the major ranking (1-based)
        major_ranking = 1
        for idx, s in enumerate(students_in_major):
            if s.student_id == student.student_id:
                major_ranking = idx + 1
                break
        
        total_students_in_major = students_in_major.count()
        
        # Only show GPA if user is superuser/staff
        show_gpa = user.is_superuser or user.is_staff
        
        results.append({
            'student': student,
            'ranking': overall_ranking,
            'total_students': total_students,
            'major_ranking': major_ranking,
            'total_students_in_major': total_students_in_major,
            'semester_display': f"{semester.title()} {year}",
            'percentage_rank': round((overall_ranking / total_students) * 100, 1) if total_students > 0 else 0,
            'major_percentage_rank': round((major_ranking / total_students_in_major) * 100, 1) if total_students_in_major > 0 else 0,
            'show_gpa': show_gpa
        })
    
    # Sort by year and semester (most recent first)
    results.sort(key=lambda x: (x['student'].year, x['student'].semester), reverse=True)
    
    return results


@login_required
def application_management(request):
    """
    Manage membership applications - view all applications with automatic rejection flags
    """
    # Device detection - block mobile and tablet devices
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    
    if user_agent.is_mobile or user_agent.is_tablet:
        return render(request, 'frontend/desktop_only.html', {
            'device_type': 'mobile device' if user_agent.is_mobile else 'tablet'
        })
    
    # Get all applications ordered by eligibility first, then by GPA and passed credits
    all_applications = Application.objects.all()
    
    # Separate eligible and rejected applications
    eligible_apps = []
    rejected_apps = []
    
    for app in all_applications:
        auto_reject = app.GPA < Decimal('3.5') or app.passed_credits < 30
        if auto_reject:
            rejected_apps.append(app)
        else:
            eligible_apps.append(app)
    
    # Sort eligible applications by GPA (highest first), then by passed credits (highest first)
    eligible_apps.sort(key=lambda x: (-x.GPA, -x.passed_credits, x.time_submitted))
    
    # Sort rejected applications by GPA (highest first), then by passed credits (highest first)
    rejected_apps.sort(key=lambda x: (-x.GPA, -x.passed_credits, x.time_submitted))
    
    # Combine lists with eligible first, then rejected
    applications = eligible_apps + rejected_apps
    
    # Add rejection flags and eligibility status to each application
    applications_with_status = []
    separator_added = False
    
    for app in applications:
        # Determine if application should be automatically rejected
        auto_reject = app.GPA < Decimal('3.5') or app.passed_credits < 30
        
        # Add separator before first rejected application
        add_separator = auto_reject and not separator_added and len([a for a in applications if not (a.GPA < Decimal('3.5') or a.passed_credits < 30)]) > 0
        if add_separator:
            separator_added = True
        
        # Determine rejection reasons
        rejection_reasons = []
        if app.GPA < Decimal('3.5'):
            rejection_reasons.append(f"GPA below 3.5 ({app.GPA})")
        if app.passed_credits < 30:
            rejection_reasons.append(f"Insufficient credits ({app.passed_credits} < 30)")
        
        # Get major display name
        major_display = dict(majors).get(app.major, app.major)
        
        applications_with_status.append({
            'application': app,
            'auto_reject': auto_reject,
            'rejection_reasons': rejection_reasons,
            'major_display': major_display,
            'eligible': not auto_reject,
            'add_separator': add_separator
        })
    
    # Calculate statistics
    total_applications = len(applications_with_status)
    eligible_applications = len([app for app in applications_with_status if app['eligible']])
    rejected_applications = total_applications - eligible_applications
    
    # Check if user can delete applications (individual and all)
    allowed_roles = ['PRESIDENT', 'VICE_PRESIDENT', 'SECRETARY']
    can_delete = request.user.is_superuser or request.user.is_staff or request.user.role in allowed_roles
    can_delete_all = can_delete  # Same permissions for both
    
    context = {
        'applications_with_status': applications_with_status,
        'total_applications': total_applications,
        'eligible_applications': eligible_applications,
        'rejected_applications': rejected_applications,
        'can_delete': can_delete,
        'can_delete_all': can_delete_all,
    }
    
    return render(request, 'frontend/application_management.html', context)


@login_required
@require_POST
def delete_application(request, application_id):
    """
    Delete a specific application - only for superstaff and specific roles
    """
    # Check if user has permission to delete applications
    allowed_roles = ['PRESIDENT', 'VICE_PRESIDENT', 'SECRETARY']
    if not (request.user.is_superuser or request.user.is_staff or request.user.role in allowed_roles):
        return JsonResponse({'success': False, 'message': 'Insufficient permissions to delete applications'})
    
    try:
        application = Application.objects.get(id=application_id)
        application.delete()
        return JsonResponse({'success': True, 'message': 'Application deleted successfully'})
    except Application.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Application not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_POST
def delete_all_applications(request):
    """
    Delete all applications - only for superstaff and specific roles
    """
    # Check if user has permission
    allowed_roles = ['PRESIDENT', 'VICE_PRESIDENT', 'SECRETARY']
    if not (request.user.is_superuser or request.user.is_staff or request.user.role in allowed_roles):
        return JsonResponse({'success': False, 'message': 'Insufficient permissions'})
    
    try:
        count = Application.objects.count()
        Application.objects.all().delete()
        return JsonResponse({'success': True, 'message': f'{count} applications deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def thread_settings(request):
    """
    Manage thread settings - accessible to any logged-in user
    """
    # Device detection - block mobile and tablet devices
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    
    if user_agent.is_mobile or user_agent.is_tablet:
        return render(request, 'frontend/desktop_only.html', {
            'device_type': 'mobile device' if user_agent.is_mobile else 'tablet'
        })
    
    # Any logged-in user can manage thread settings
    settings = ThreadSettings.get_settings()
    message = None
    error_message = None
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'toggle_threads':
            settings.allow_new_threads = not settings.allow_new_threads
            settings.updated_by = request.user
            settings.save()
            
            status = "enabled" if settings.allow_new_threads else "disabled"
            message = f"Thread creation has been {status}."
            
        elif action == 'update_message':
            new_message = request.POST.get('closure_message', '').strip()
            if new_message:
                settings.closure_message = new_message
                settings.updated_by = request.user
                settings.save()
                message = "Closure message updated successfully."
            else:
                error_message = "Closure message cannot be empty."
    
    # Get thread statistics
    total_threads = Thread.objects.count()
    total_replies = Reply.objects.count()
    recent_threads = Thread.objects.filter(
        created_at__gte=datetime.now() - timedelta(days=7)
    ).count()
    
    context = {
        'settings': settings,
        'message': message,
        'error_message': error_message,
        'total_threads': total_threads,
        'total_replies': total_replies,
        'recent_threads': recent_threads,
    }
    
    return render(request, 'frontend/thread_settings.html', context)


def contact(request):
    """
    Contact page with thread system - accessible to everyone (logged in or not)
    Shows all threads and allows creating new threads (if enabled)
    """
    settings = ThreadSettings.get_settings()
    
    if request.method == 'POST':
        # Check if thread creation is allowed
        if not settings.allow_new_threads:
            context = {
                'error_message': settings.closure_message,
                'title': request.POST.get('title', ''),
                'content': request.POST.get('content', ''),
                'threads_disabled': True,
                'settings': settings
            }
            return render(request, 'frontend/contact.html', context)
        
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        
        if title and content:
            # Create new thread
            thread = Thread.objects.create(
                title=title,
                content=content
            )
            return redirect('contact')
        else:
            # Handle validation error
            context = {
                'error_message': 'Both title and content are required.',
                'title': title,
                'content': content,
                'settings': settings
            }
            return render(request, 'frontend/contact.html', context)
    
    # Get all threads ordered by creation date (newest first)
    all_threads = Thread.objects.all().order_by('-created_at')
    
    # Pagination - 6 threads per page
    paginator = Paginator(all_threads, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add reply count, latest reply info, and first reply to each thread
    threads_with_info = []
    for thread in page_obj:
        reply_count = thread.replies.count()
        latest_reply = thread.get_latest_reply()
        first_reply = thread.replies.order_by('created_at').first()
        
        threads_with_info.append({
            'thread': thread,
            'reply_count': reply_count,
            'latest_reply': latest_reply,
            'first_reply': first_reply,
        })
    
    context = {
        'threads_with_info': threads_with_info,
        'page_obj': page_obj,
        'user_is_staff': request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser),
        'user_can_delete': request.user.is_authenticated and (request.user.is_member or request.user.is_staff or request.user.is_superuser),
        'settings': settings,
    }
    
    return render(request, 'frontend/contact.html', context)


def thread_detail(request, thread_id):
    """
    View individual thread with all replies
    """
    thread = get_object_or_404(Thread, id=thread_id)
    replies = thread.replies.all().order_by('created_at')
    
    context = {
        'thread': thread,
        'replies': replies,
        'user_can_reply': request.user.is_authenticated and isinstance(request.user, User),
        'user_can_delete': request.user.is_authenticated and (request.user.is_member or request.user.is_staff or request.user.is_superuser),
    }
    
    return render(request, 'frontend/thread_detail.html', context)


@login_required
@require_POST
def add_reply(request, thread_id):
    """
    Add a reply to a thread - only for logged in Users
    """
    thread = get_object_or_404(Thread, id=thread_id)
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'success': False, 'message': 'Reply content is required'})
    
    # Only allow Users (from our custom model) to reply
    if not isinstance(request.user, User):
        return JsonResponse({'success': False, 'message': 'Only registered members can reply'})
    
    try:
        reply = Reply.objects.create(
            thread=thread,
            user=request.user,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Reply added successfully',
            'reply_id': reply.id,
            'user_name': request.user.get_full_name(),
            'created_at': reply.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'content': reply.content
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_POST
def delete_thread(request, thread_id):
    """
    Delete a thread and all its replies - only for members
    """
    # Check if user is a member
    if not (request.user.is_member or request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'message': 'Only members can delete threads'})
    
    try:
        thread = get_object_or_404(Thread, id=thread_id)
        thread_title = thread.title
        
        # Delete the thread (this will also delete all replies due to cascade)
        thread.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Thread "{thread_title}" and all its replies have been deleted successfully'
        })
        
    except Thread.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Thread not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_POST
def delete_reply(request, reply_id):
    """
    Delete a specific reply - only for members
    """
    # Check if user is a member
    if not (request.user.is_member or request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'message': 'Only members can delete replies'})
    
    try:
        reply = get_object_or_404(Reply, id=reply_id)
        thread_id = reply.thread.id
        
        # Delete the reply
        reply.delete()
        
        return JsonResponse({
            'success': True, 
            'message': 'Reply deleted successfully',
            'thread_id': thread_id
        })
        
    except Reply.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Reply not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def custom_404_view(request, exception=None):
    """
    Custom 404 error handler - works both as error handler and regular view
    """
    return render(request, 'frontend/404.html', status=404)


def events_list(request):
    """List upcoming and past events"""
    try:
        from .models import Event
        # Show events in the order they were added (newest first)
        qs = Event.objects.all().order_by('-created_at')
        paginator = Paginator(qs, 9)  # 9 events per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        events = page_obj.object_list
    except Exception:
        page_obj = None
        events = []

    return render(request, 'frontend/events_list.html', {'events': events, 'page_obj': page_obj})


def event_detail(request, pk):
    """Show event details"""
    from django.shortcuts import get_object_or_404
    from datetime import datetime
    try:
        from .models import Event
        event = get_object_or_404(Event, pk=pk)
    except Exception:
        event = None

    # Check if registration is allowed (allowed before and during event, blocked after end)
    registration_allowed = False
    if event:
        now = datetime.utcnow()
        end_date = event.end_date or event.start_date
        end_time = event.end_time or event.start_time or datetime.max.time()
        event_end = datetime.combine(end_date, end_time)
        
        # Allow registration before event starts and during event, block after event ends
        registration_allowed = now <= event_end

    # If the attendance form was submitted, handle it here
    if request.method == 'POST':
        # Check if registration is allowed
        if not registration_allowed:
            messages.error(request, 'Registration is closed. This event has already ended.')
            return render(request, 'frontend/event_detail.html', {'event': event, 'registration_allowed': registration_allowed})
        
        try:
            from .models import Attendance
        except Exception:
            messages.error(request, 'Attendance model not available')
            return render(request, 'frontend/event_detail.html', {'event': event, 'registration_allowed': registration_allowed})

        student_id = request.POST.get('student_id', '').strip()
        student_name = request.POST.get('student_name', '').strip()
        student_email = request.POST.get('email', '').strip()

        if not student_id or not student_name:
            messages.error(request, 'Student ID and name are required.')
            return render(request, 'frontend/event_detail.html', {'event': event, 'registration_allowed': registration_allowed})

        # If an attendance record for this event+student exists, return the same code
        existing = Attendance.objects.filter(event=event, student_id=student_id).first()
        if existing:
            code = existing.code
            return render(request, 'frontend/event_code.html', {'event': event, 'student_id': student_id, 'student_name': student_name, 'code': code, 'existing': True})

        # Generate and persist a unique 6-digit code for this event in a DB-safe way.
        # We try to create the Attendance with a candidate code; on IntegrityError
        # we retry (this avoids the check-then-create race condition).
        import random
        from django.db import IntegrityError as DjangoIntegrityError
        from datetime import datetime

        code = None
        max_attempts = 20
        for attempt in range(max_attempts):
            candidate = f"{random.randint(0, 999999):06d}"
            try:
                attendance = Attendance.objects.create(
                    event=event,
                    student_id=student_id,
                    student_name=student_name,
                    email=student_email or None,
                    code=candidate,
                )
                code = candidate
                created = True
                break
            except DjangoIntegrityError:
                # Could be a collision on (event, code) or (event, student_id).
                # If student record appeared concurrently, reuse it.
                existing = Attendance.objects.filter(event=event, student_id=student_id).first()
                if existing:
                    code = existing.code
                    return render(request, 'frontend/event_code.html', {'event': event, 'student_id': student_id, 'student_name': student_name, 'code': code, 'existing': True})
                # Otherwise assume code collision and retry
                continue
        else:
            # fallback to a timestamp-based code if we couldn't get a unique 6-digit code
            candidate = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            try:
                attendance = Attendance.objects.create(
                    event=event,
                    student_id=student_id,
                    student_name=student_name,
                    email=student_email or None,
                    code=candidate,
                )
                code = candidate
            except Exception:
                # If still failing, try to find an existing record (last resort)
                existing = Attendance.objects.filter(event=event, student_id=student_id).first()
                if existing:
                    code = existing.code
                    return render(request, 'frontend/event_code.html', {'event': event, 'student_id': student_id, 'student_name': student_name, 'code': code, 'existing': True})
                messages.error(request, 'Could not register attendance at this time.')
                return render(request, 'frontend/event_detail.html', {'event': event, 'registration_allowed': registration_allowed})

        return render(request, 'frontend/event_code.html', {'event': event, 'student_id': student_id, 'student_name': student_name, 'code': code, 'existing': False})

    return render(request, 'frontend/event_detail.html', {'event': event, 'registration_allowed': registration_allowed})


def verify_start(request, a, b, c):
    """Dynamic route: given three preset numbers, find the event with those secrets,
    render a template to enter the attendee's code, and on POST set present_start=True
    if (and only if) the event has started (date+time)."""
    try:
        from .models import Event, Attendance
    except Exception:
        return HttpResponseBadRequest('Models not available')

    mode = 'start'
    # Find the event matching the three start secret numbers
    event = Event.objects.filter(secret_start_a=a, secret_start_b=b, secret_start_c=c).first()
    if not event:
        return render(request, 'frontend/verify_not_found.html', {'a': a, 'b': b, 'c': c, 'mode': mode})

    context = {
        'event': event,
        'mode': mode,
    }

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        if not code:
            messages.error(request, 'Code is required')
            return render(request, 'frontend/verify_start.html', context)

        # Lookup attendance by event + code
        attendance = Attendance.objects.filter(event=event, code=code).first()
        if not attendance:
            messages.error(request, 'Invalid code')
            return render(request, 'frontend/verify_start.html', context)

        # Check if event has started (compare date and time). If start_time is null, compare date only.
        now = datetime.utcnow()
        event_start = datetime.combine(event.start_date, event.start_time or datetime.min.time())

        # If the event has started, record start attendance
        if now >= event_start:
            if not attendance.present_start:
                attendance.present_start = True
                attendance.save(update_fields=['present_start'])
            success_context = {
                'event': event,
                'attendance': attendance,
                'mode': mode,
            }
            return render(request, 'frontend/verify_success.html', success_context)
        else:
            messages.error(request, 'Event has not started yet')
            return render(request, 'frontend/verify_start.html', context)

    return render(request, 'frontend/verify_start.html', context)


def verify_end(request, a, b, c):
    """Same as verify_start but for the end attendance triplet. For now we only
    implement setting present_end later; this route will mirror start logic but
    target the secret_end_* fields."""
    try:
        from .models import Event, Attendance, EventSection
    except Exception:
        return HttpResponseBadRequest('Models not available')

    mode = 'end'
    event = Event.objects.filter(secret_end_a=a, secret_end_b=b, secret_end_c=c).first()
    if not event:
        return render(request, 'frontend/verify_not_found.html', {'a': a, 'b': b, 'c': c, 'mode': mode})

    # Get sections for this event
    sections = EventSection.objects.filter(event=event).order_by('section_code')
    
    context = {
        'event': event,
        'mode': mode,
        'sections': sections,
    }

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        if not code:
            messages.error(request, 'Code is required')
            return render(request, 'frontend/verify_start.html', context)

        attendance = Attendance.objects.filter(event=event, code=code).first()
        if not attendance:
            messages.error(request, 'Invalid code')
            return render(request, 'frontend/verify_start.html', context)
        
        # Add currently selected section IDs to context for pre-checking checkboxes
        context['selected_section_ids'] = list(attendance.sections.values_list('id', flat=True))

        # Determine when end attendance should be allowed. Prefer event end date/time,
        # fall back to start date/time if end info is missing.
        now = datetime.utcnow()
        end_date = event.end_date or event.start_date
        if event.end_time:
            end_time = event.end_time
        elif event.start_time:
            end_time = event.start_time
        else:
            end_time = datetime.min.time()
        event_end = datetime.combine(end_date, end_time)

        if now >= event_end:
            if not attendance.present_end:
                attendance.present_end = True
                attendance.save(update_fields=['present_end'])
            
            # Handle section selection
            selected_section_ids = request.POST.getlist('sections')
            if selected_section_ids:
                attendance.sections.set(selected_section_ids)
            
            success_context = {
                'event': event,
                'attendance': attendance,
                'mode': mode,
            }
            return render(request, 'frontend/verify_success.html', success_context)
        else:
            messages.error(request, 'Event has not ended yet')
            return render(request, 'frontend/verify_start.html', context)

    return render(request, 'frontend/verify_start.html', context)


@login_required
def attendance_qr(request, pk):
    """Member-only page that shows QR links for start and end attendance verification.
    
    The QR codes encode URLs pointing to verify_start and verify_end views with the
    event's three secret numbers as path parameters. For example:
    - Start QR: /events/verify/start/123456/789012/345678/
    - End QR: /events/verify/end/234567/890123/456789/
    
    The QR images are generated using Google Charts API (no external libraries required).
    When attendees scan the QR, they're taken to the verify page where they enter their
    6-digit attendance code to mark their start or end attendance.
    """
    try:
        from .models import Event
    except Exception:
        return HttpResponseBadRequest('Models not available')

    event = get_object_or_404(Event, pk=pk)

    if not (getattr(request.user, 'is_member', False) or request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden('Permission denied')

    # Build verify URLs
    start_ok = event.secret_start_a is not None and event.secret_start_b is not None and event.secret_start_c is not None
    end_ok = event.secret_end_a is not None and event.secret_end_b is not None and event.secret_end_c is not None

    start_url = None
    end_url = None
    if start_ok:
        start_url = request.build_absolute_uri(reverse('verify_start', args=(event.secret_start_a, event.secret_start_b, event.secret_start_c)))
    if end_ok:
        end_url = request.build_absolute_uri(reverse('verify_end', args=(event.secret_end_a, event.secret_end_b, event.secret_end_c)))

    # Generate QR image URLs using QR Server API (Google Charts API is deprecated)
    def qr_img_url(target):
        # URL-encode the target to ensure special characters are properly handled
        encoded_target = quote(target, safe='')
        # Using api.qrserver.com - a free, reliable QR code API
        return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_target}"

    context = {
        'event': event,
        'start_url': start_url,
        'end_url': end_url,
        'start_qr': qr_img_url(start_url) if start_url else None,
        'end_qr': qr_img_url(end_url) if end_url else None,
    }

    return render(request, 'frontend/attendance_qr.html', context)



@login_required
def create_event(request):
    """Allow portal members to create an event. Only users with is_member True or staff are allowed."""
    # permission check
    if not (request.user.is_authenticated and (request.user.is_staff or getattr(request.user, 'is_member', False))):
        messages.error(request, 'You do not have permission to create events.')
        return redirect('portal')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Event "{event.title}" created successfully.')
            return redirect('events')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EventForm()

    return render(request, 'frontend/create_event.html', {'form': form})


@login_required
def manage_event_sections(request, pk):
    """Allow members to add/edit/delete professors and sections for an event."""
    if not (getattr(request.user, 'is_member', False) or request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to manage event sections.')
        return redirect('portal')
    
    try:
        from .models import Event, EventSection
    except Exception:
        messages.error(request, 'Models not available')
        return redirect('portal')
    
    event = get_object_or_404(Event, pk=pk)
    sections = EventSection.objects.filter(event=event).order_by('section_code')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            professor_name = request.POST.get('professor_name', '').strip()
            section_code = request.POST.get('section_code', '').strip()
            
            if professor_name and section_code:
                try:
                    EventSection.objects.create(
                        event=event,
                        professor_name=professor_name,
                        section_code=section_code
                    )
                    messages.success(request, f'Section "{section_code}" added successfully.')
                except Exception as e:
                    messages.error(request, f'Error adding section: {str(e)}')
            else:
                messages.error(request, 'Professor name and section code are required.')
        
        elif action == 'delete':
            section_id = request.POST.get('section_id')
            if section_id:
                try:
                    section = EventSection.objects.get(pk=section_id, event=event)
                    section_name = str(section)
                    section.delete()
                    messages.success(request, f'Section "{section_name}" deleted.')
                except EventSection.DoesNotExist:
                    messages.error(request, 'Section not found.')
                except Exception as e:
                    messages.error(request, f'Error deleting section: {str(e)}')
        
        return redirect('manage_event_sections', pk=event.pk)
    
    return render(request, 'frontend/manage_event_sections.html', {
        'event': event,
        'sections': sections
    })


def image_proxy(request):
    """Simple image proxy for a small set of allowed hosts.

    Use: /image-proxy/?url=<encoded_url>
    This avoids embedding issues when third-party hosts send restrictive CORP/CSP headers.
    """
    url = request.GET.get('url')
    if not url:
        return HttpResponseBadRequest('Missing url')

    parsed = urlparse(url)
    host = parsed.netloc.lower()

    # Whitelist hosts known to be safe for proxying. Adjust as needed.
    allowed_hosts = [
        'photos.fife.usercontent.google.com',
        'lh3.googleusercontent.com',
        'drive.google.com'
    ]

    if host not in allowed_hosts:
        return HttpResponseBadRequest('Host not allowed')

    try:
        resp = requests.get(url, stream=True, timeout=10)
    except Exception as e:
        return HttpResponseBadRequest('Error fetching image')

    if resp.status_code != 200:
        return HttpResponseBadRequest('Upstream returned %s' % resp.status_code)

    content_type = resp.headers.get('Content-Type', 'application/octet-stream')
    data = resp.content

    response = HttpResponse(data, content_type=content_type)
    # We explicitly don't forward CSP/CORP headers from upstream.
    # Allow caching by the browser for a short time; adjust Cache-Control as you prefer.
    response['Cache-Control'] = 'public, max-age=3600'
    return response


@login_required
@require_POST
def delete_event(request, event_id):
    """Allow members or staff to delete an event from the portal."""
    # permission: staff or member
    if not (request.user.is_staff or getattr(request.user, 'is_member', False)):
        return HttpResponseBadRequest('Permission denied')
    # Import Event from local models and fetch
    try:
        from .models import Event
    except Exception:
        return HttpResponseBadRequest('Event model not available')

    event = get_object_or_404(Event, pk=event_id)
    title = event.title
    event.delete()
    messages.success(request, f'Event "{title}" deleted.')
    return redirect('portal')


@login_required
def events_dashboard(request):
    """Events dashboard for members to view all events and attendance data."""
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    # Check member permission
    if not (getattr(request.user, 'is_member', False) or request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access the events dashboard.')
        return redirect('portal')
    
    # Device detection - block mobile and tablet devices
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    if user_agent.is_mobile or user_agent.is_tablet:
        return render(request, 'frontend/desktop_only.html', {
            'device_type': 'mobile device' if user_agent.is_mobile else 'tablet'
        })
    
    try:
        from .models import Event, Attendance
        from datetime import datetime
        
        events = Event.objects.all().order_by('-start_date')
        
        # Add attendance stats and status to each event
        events_with_stats = []
        now = datetime.now().date()
        
        for event in events:
            # Determine event status
            if event.end_date < now:
                status = 'past'
            elif event.start_date > now:
                status = 'upcoming'
            else:
                status = 'ongoing'
            
            # Get attendance stats
            attendances = Attendance.objects.filter(event=event)
            total = attendances.count()
            start_count = attendances.filter(present_start=True).count()
            end_count = attendances.filter(present_end=True).count()
            
            event.status = status
            event.total_registered = total
            event.start_attendance = start_count
            event.end_attendance = end_count
            
            events_with_stats.append(event)
        
        return render(request, 'frontend/events_dashboard.html', {
            'events': events_with_stats
        })
    except Exception as e:
        messages.error(request, f'Error loading events dashboard: {str(e)}')
        return redirect('portal')


@login_required
def event_attendance_data(request, pk):
    """API endpoint to fetch attendance data for a specific event."""
    if not (getattr(request.user, 'is_member', False) or request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        from .models import Event, Attendance
        
        event = get_object_or_404(Event, pk=pk)
        filter_type = request.GET.get('filter', 'all')
        
        # Get all attendances for the event
        attendances = Attendance.objects.filter(event=event).order_by('student_name')
        
        # Apply filters
        if filter_type == 'start':
            attendances = attendances.filter(present_start=True)
        elif filter_type == 'end':
            attendances = attendances.filter(present_end=True)
        elif filter_type == 'both':
            attendances = attendances.filter(present_start=True, present_end=True)
        
        # Calculate statistics
        all_attendances = Attendance.objects.filter(event=event)
        total = all_attendances.count()
        start_only = all_attendances.filter(present_start=True, present_end=False).count()
        end_only = all_attendances.filter(present_start=False, present_end=True).count()
        both = all_attendances.filter(present_start=True, present_end=True).count()
        
        # Format attendance data
        attendance_list = []
        for att in attendances:
            # Get sections for this attendance
            sections_list = [f"{s.section_code} ({s.professor_name})" for s in att.sections.all()]
            
            attendance_list.append({
                'student_id': att.student_id,
                'student_name': att.student_name,
                'email': att.email or '',
                'code': att.code,
                'present_start': att.present_start,
                'present_end': att.present_end,
                'sections': ', '.join(sections_list) if sections_list else 'N/A',
            })
        
        return JsonResponse({
            'stats': {
                'total': total,
                'start_only': start_only,
                'end_only': end_only,
                'both': both,
            },
            'attendances': attendance_list
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def export_event_sections(request, pk):
    """Export event attendance data organized by sections to Excel files (one per section)."""
    if not (getattr(request.user, 'is_member', False) or request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to export attendance data.')
        return redirect('events_dashboard')
    
    try:
        from .models import Event, EventSection, Attendance
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from django.http import HttpResponse
        from io import BytesIO
        import zipfile
        
        event = get_object_or_404(Event, pk=pk)
        sections = EventSection.objects.filter(event=event).order_by('section_code')
        
        if not sections.exists():
            messages.error(request, 'No sections found for this event.')
            return redirect('events_dashboard')
        
        # Create a zip file to hold multiple Excel files (one per section)
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
            for section in sections:
                # Create a new workbook for each section
                wb = Workbook()
                ws = wb.active
                ws.title = f"{section.section_code[:25]}"  # Excel sheet name limit is 31 chars
                
                # Title
                ws.merge_cells('A1:E1')
                title_cell = ws['A1']
                title_cell.value = f"{event.title} - Attendance Report"
                title_cell.font = Font(bold=True, size=14, color="FFFFFF")
                title_cell.fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
                title_cell.alignment = Alignment(horizontal='center', vertical='center')
                ws.row_dimensions[1].height = 30
                
                # Section info
                ws.merge_cells('A2:E2')
                section_cell = ws['A2']
                section_cell.value = f"Section: {section.section_code} - Professor: {section.professor_name}"
                section_cell.font = Font(bold=True, size=12, color="FFFFFF")
                section_cell.fill = PatternFill(start_color="3498DB", end_color="3498DB", fill_type="solid")
                section_cell.alignment = Alignment(horizontal='center', vertical='center')
                ws.row_dimensions[2].height = 25
                
                # Event date info
                ws.merge_cells('A3:E3')
                date_cell = ws['A3']
                date_str = f"Event Date: {event.start_date}"
                if event.end_date and event.end_date != event.start_date:
                    date_str += f" to {event.end_date}"
                date_cell.value = date_str
                date_cell.font = Font(italic=True, size=10)
                date_cell.alignment = Alignment(horizontal='center')
                ws.row_dimensions[3].height = 20
                
                # Headers
                headers = ['Student ID', 'Student Name', 'Email', 'Attended Start', 'Attended End']
                header_fill = PatternFill(start_color="34495E", end_color="34495E", fill_type="solid")
                header_font = Font(bold=True, color="FFFFFF", size=11)
                border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
                
                for col_num, header in enumerate(headers, 1):
                    cell = ws.cell(row=5, column=col_num)
                    cell.value = header
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    cell.border = border
                ws.row_dimensions[5].height = 25
                
                # Get attendances for this section
                attendances = Attendance.objects.filter(
                    event=event,
                    sections=section
                ).order_by('student_name')
                
                # Data rows
                row_num = 6
                for att in attendances:
                    ws.cell(row=row_num, column=1, value=att.student_id).border = border
                    ws.cell(row=row_num, column=2, value=att.student_name).border = border
                    ws.cell(row=row_num, column=3, value=att.email or 'N/A').border = border
                    
                    # Attended Start - Yes/No
                    start_cell = ws.cell(row=row_num, column=4, value='Yes' if att.present_start else 'No')
                    start_cell.border = border
                    start_cell.alignment = Alignment(horizontal='center')
                    if att.present_start:
                        start_cell.font = Font(color="27AE60", bold=True)
                    else:
                        start_cell.font = Font(color="E74C3C", bold=True)
                    
                    # Attended End - Yes/No
                    end_cell = ws.cell(row=row_num, column=5, value='Yes' if att.present_end else 'No')
                    end_cell.border = border
                    end_cell.alignment = Alignment(horizontal='center')
                    if att.present_end:
                        end_cell.font = Font(color="27AE60", bold=True)
                    else:
                        end_cell.font = Font(color="E74C3C", bold=True)
                    
                    row_num += 1
                
                # Add summary row
                ws.merge_cells(f'A{row_num + 1}:C{row_num + 1}')
                summary_cell = ws.cell(row=row_num + 1, column=1)
                summary_cell.value = f"Total Students: {attendances.count()}"
                summary_cell.font = Font(bold=True, size=11)
                summary_cell.alignment = Alignment(horizontal='left')
                
                # Adjust column widths
                ws.column_dimensions['A'].width = 15
                ws.column_dimensions['B'].width = 30
                ws.column_dimensions['C'].width = 30
                ws.column_dimensions['D'].width = 18
                ws.column_dimensions['E'].width = 18
                
                # Save workbook to bytes
                excel_buffer = BytesIO()
                wb.save(excel_buffer)
                excel_buffer.seek(0)
                
                # Add to zip file
                safe_section_name = "".join(c for c in section.section_code if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_prof_name = "".join(c for c in section.professor_name if c.isalnum() or c in (' ', '-', '_')).strip()
                filename = f"{safe_section_name}_{safe_prof_name}.xlsx"
                zip_file.writestr(filename, excel_buffer.getvalue())
        
        # Prepare response
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        safe_event_name = "".join(c for c in event.title if c.isalnum() or c in (' ', '-', '_')).strip()
        response['Content-Disposition'] = f'attachment; filename="{safe_event_name}_Attendance_by_Section.zip"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting attendance data: {str(e)}')
        return redirect('events_dashboard')


@login_required
def backup_database(request):
    """Download the SQLite database file as a backup."""
    # Only superuser or staff can backup database
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, 'You do not have permission to backup the database.')
        return redirect('portal')
    
    try:
        from django.conf import settings
        from datetime import datetime
        import os
        
        # Get the database path
        db_path = settings.DATABASES['default']['NAME']
        
        # Check if using SQLite
        if 'sqlite' not in settings.DATABASES['default']['ENGINE']:
            messages.error(request, 'Database backup is only available for SQLite databases.')
            return redirect('portal')
        
        # Check if database file exists
        if not os.path.exists(db_path):
            messages.error(request, 'Database file not found.')
            return redirect('portal')
        
        # Read the database file
        with open(db_path, 'rb') as db_file:
            db_content = db_file.read()
        
        # Create response with database file
        response = HttpResponse(db_content, content_type='application/x-sqlite3')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="dlc_database_backup_{timestamp}.sqlite3"'
        
        messages.success(request, f'Database backup downloaded successfully!')
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error backing up database: {str(e)}')
        return redirect('portal')


@login_required
def restore_database(request):
    """Restore database from an uploaded SQLite file."""
    # Only superuser or staff can restore database
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, 'You do not have permission to restore the database.')
        return redirect('portal')
    
    # Device detection - block mobile and tablet devices
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    if user_agent.is_mobile or user_agent.is_tablet:
        return render(request, 'frontend/desktop_only.html', {
            'device_type': 'mobile device' if user_agent.is_mobile else 'tablet'
        })
    
    if request.method == 'POST':
        try:
            from django.conf import settings
            from datetime import datetime
            import os
            import shutil
            
            # Get the uploaded file
            uploaded_file = request.FILES.get('database_file')
            
            if not uploaded_file:
                messages.error(request, 'No file uploaded.')
                return render(request, 'frontend/restore_database.html')
            
            # Validate file extension
            if not uploaded_file.name.endswith(('.sqlite3', '.db', '.sqlite')):
                messages.error(request, 'Invalid file type. Please upload a SQLite database file (.sqlite3, .db, or .sqlite).')
                return render(request, 'frontend/restore_database.html')
            
            # Get the database path
            db_path = settings.DATABASES['default']['NAME']
            
            # Check if using SQLite
            if 'sqlite' not in settings.DATABASES['default']['ENGINE']:
                messages.error(request, 'Database restore is only available for SQLite databases.')
                return render(request, 'frontend/restore_database.html')
            
            # Create a backup of the current database before restoring
            backup_dir = os.path.join(settings.BASE_DIR, 'database_backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'auto_backup_before_restore_{timestamp}.sqlite3')
            
            # Copy current database as backup
            shutil.copy2(db_path, backup_path)
            
            # Write the uploaded file to the database location
            with open(db_path, 'wb') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            messages.success(request, f'Database restored successfully! A backup of the previous database was saved.')
            messages.info(request, f'Backup location: {backup_path}')
            
            # Redirect to login (user will need to log in again with restored credentials)
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error restoring database: {str(e)}')
            return render(request, 'frontend/restore_database.html')
    
    # GET request - show the upload form
    return render(request, 'frontend/restore_database.html')

