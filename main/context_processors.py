from .models import User, DeanList, DeanListStudent, Application

def user_stats(request):
    """
    Context processor to add user statistics to all templates.
    """
    # Get the most recent dean's list
    latest_dean_list = DeanList.objects.order_by('-created_at').first()
    
    # Count students in the latest dean's list only
    latest_dean_list_students = 0
    if latest_dean_list:
        latest_dean_list_students = DeanListStudent.objects.filter(dean_list=latest_dean_list).count()
    
    # Count pending applications
    pending_applications = Application.objects.count()
    
    return {
        'pending_applications': pending_applications,
        'member_count': User.objects.filter(is_member=True).count(),
        'dean_list_count': DeanList.objects.count(),
        'total_dean_list_students': latest_dean_list_students,
    }
