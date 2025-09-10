from django.db import models
from django.contrib.auth.models import AbstractUser

majors = [
    ('FIN', 'Finance'),
    ('MIS', 'Management Information Systems'),
    ('MKT', 'Marketing'),
    ('MGT', 'Management'),
    ('ACC', 'Accounting'),
    ('ECO', 'Economics'),
    ('PMGT', 'Public Management'),
    ('OM', 'Operations Management'),

]
roles = [
    ('MEMBER', 'Member'),
    ('SECRETARY', 'General Secretary'),
    ('PRESIDENT', 'President'),
    ('VICE_PRESIDENT', 'Vice President'),
    ('TREASURER', 'Treasurer'),
]

# Create your models here.
class Application(models.Model):
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    time_submitted = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    passed_credits = models.IntegerField()
    GPA = models.DecimalField(max_digits=3, decimal_places=2)
    major = models.CharField(max_length=4, choices=majors)
    anything_else = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.CharField(max_length=20, choices=roles)
    is_member = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)


class DeanList(models.Model):
    SEMESTER_CHOICES = [
        ('fall', 'Fall'),
        ('spring', 'Spring'),
    ]
    
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    year = models.IntegerField()
    excel_file = models.FileField(upload_to='dean_list_excel_files/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['semester', 'year']  # Prevent duplicate semester/year combinations
    
    def __str__(self):
        return f"{self.semester.title()} {self.year} Dean's List"


class DeanListStudent(models.Model):
    student_id = models.CharField(max_length=20)
    student_name = models.CharField(max_length=200)
    student_major = models.CharField(max_length=50)
    semester = models.CharField(max_length=10)
    year = models.IntegerField()
    gpa = models.DecimalField(max_digits=3, decimal_places=2)
    passed_credits = models.IntegerField()
    registered_credits = models.IntegerField()
    dean_list = models.ForeignKey(DeanList, on_delete=models.CASCADE, related_name='students')
    def __str__(self):
        return f"{self.student_name} - {self.semester} {self.year}"


class Thread(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']  # Most recent threads first
    
    def __str__(self):
        return f"Thread: {self.title[:50]}..."
    
    def get_latest_reply(self):
        """Get the most recent reply for this thread"""
        return self.replies.order_by('-created_at').first()


class Reply(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']  # Oldest replies first within a thread
    
    def __str__(self):
        return f"Reply by {self.user.get_full_name()} to {self.thread.title[:30]}..."


class ThreadSettings(models.Model):
    """
    Singleton model to store thread/contact system settings
    """
    allow_new_threads = models.BooleanField(default=True)
    closure_message = models.TextField(
        default="Thread creation is temporarily disabled. Please check back later.",
        blank=True,
        help_text="Message to display when thread creation is disabled"
    )
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "Thread Settings"
        verbose_name_plural = "Thread Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Prevent deletion of the singleton instance
        pass
    
    @classmethod
    def get_settings(cls):
        """Get the singleton instance, create if doesn't exist"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        status = "Open" if self.allow_new_threads else "Closed"
        return f"Thread Creation: {status}"
