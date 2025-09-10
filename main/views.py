
from .models import Application, User, DeanListStudent, DeanList, Thread, Reply, ThreadSettings, majors
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
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
import random
from decimal import Decimal
import os
from django.db.models import Q

def home(request):
    return render(request, 'frontend/index.html')

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
    return render(request, 'frontend/portal.html', {'user': request.user})


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
    
    if request.method == "POST" and can_add_member:
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
        'role_choices': role_choices,
        'user': request.user,
    }
    
    return render(request, 'frontend/add_member.html', context)


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
                'years': range(2012, 2046) 
            }
            return render(request, 'frontend/newdl.html', context)
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            context = {
                'message': 'Please upload a valid Excel file (.xlsx or .xls).',
                'years': range(2012, 2046)
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
                'years': range(2012, 2046)
            }) 
            
        except Exception as e:
            context = {
                'message': f'Error creating dean\'s list: {str(e)}',
                'years': range(2012, 2046)
            }
            return render(request, 'frontend/newdl.html', context)

    context = {
        'years': range(2012, 2046)  
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
            ).order_by('student_major', '-gpa', 'student_name')
            
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
    
    context = {
        'available_lists': available_lists,
        'all_majors': sorted(available_majors),
        'students_by_major': students_by_major,
        'selected_semester': selected_semester,
        'selected_year': selected_year,
        'selected_major': selected_major,
        'years': range(2012, 2046),
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

