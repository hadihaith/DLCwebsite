import random

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


class Course(models.Model):
    """Model to store course information from CMU syllabus system"""
    course_id = models.CharField(max_length=20, unique=True, help_text="Course ID (e.g., FIN301)")
    course_name = models.CharField(max_length=255, help_text="Full course name")
    syllabus_url = models.URLField(blank=True, null=True, help_text="Direct download link to syllabus PDF")
    info_url = models.URLField(blank=True, null=True, help_text="URL to course info page")
    department = models.CharField(max_length=10, blank=True, null=True, help_text="Department code (FIN, MKT, etc.)")
    credits = models.IntegerField(blank=True, null=True, help_text="Number of credit hours")
    is_active = models.BooleanField(default=True, help_text="Whether the course is currently offered")
    last_updated = models.DateTimeField(auto_now=True, help_text="Last time the course data was updated")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['course_id']
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return f"{self.course_id} - {self.course_name}"

    @property
    def department_name(self):
        """Get full department name from department code"""
        dept_mapping = {
            'ACC': 'Accounting',
            'ECON': 'Economics', 
            'ELU': 'English Language Unit',
            'FIN': 'Finance',
            'ISOM': 'Information Systems & Operations Management',
            'MBA': 'Master of Business Administration',
            'MGTMKT': 'Management & Marketing',
            'PA': 'Public Administration',
            # Legacy mappings
            'MKT': 'Marketing', 
            'MGT': 'Management',
            'ECO': 'Economics',
            'MIS': 'Management Information Systems',
            'PMGT': 'Public Management',
            'OM': 'Operations Management',
        }
        return dept_mapping.get(self.department, self.department or 'Unknown')


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    image_url = models.URLField(blank=True, null=True)
    # Optional preset secret numbers used to generate dynamic verification routes
    # Three numbers for start attendance verification and three for end attendance verification
    secret_start_a = models.IntegerField(null=True, blank=True)
    secret_start_b = models.IntegerField(null=True, blank=True)
    secret_start_c = models.IntegerField(null=True, blank=True)
    secret_end_a = models.IntegerField(null=True, blank=True)
    secret_end_b = models.IntegerField(null=True, blank=True)
    secret_end_c = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date', 'start_time']

    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"

    def _generate_triplet(self):
        return tuple(random.randint(100000, 999999) for _ in range(3))

    def save(self, *args, **kwargs):
        # Only set secrets when creating new events or when any value is missing
        if not self.pk:
            if self.secret_start_a is None or self.secret_start_b is None or self.secret_start_c is None:
                self.secret_start_a, self.secret_start_b, self.secret_start_c = self._generate_triplet()
            if self.secret_end_a is None or self.secret_end_b is None or self.secret_end_c is None:
                self.secret_end_a, self.secret_end_b, self.secret_end_c = self._generate_triplet()
        else:
            # For existing events, backfill any missing values without changing existing ones
            if self.secret_start_a is None or self.secret_start_b is None or self.secret_start_c is None:
                a, b, c = self._generate_triplet()
                self.secret_start_a = self.secret_start_a or a
                self.secret_start_b = self.secret_start_b or b
                self.secret_start_c = self.secret_start_c or c
            if self.secret_end_a is None or self.secret_end_b is None or self.secret_end_c is None:
                a, b, c = self._generate_triplet()
                self.secret_end_a = self.secret_end_a or a
                self.secret_end_b = self.secret_end_b or b
                self.secret_end_c = self.secret_end_c or c

        super().save(*args, **kwargs)


class EventSection(models.Model):
    """Sections/classes associated with an event (e.g., ACC201-001, FIN305-002)"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sections')
    professor_name = models.CharField(max_length=200)
    section_code = models.CharField(max_length=50, help_text="e.g., ACC201-001 or Section 1")
    
    class Meta:
        ordering = ['section_code']
        unique_together = ('event', 'section_code')
    
    def __str__(self):
        return f"{self.section_code} - {self.professor_name}"


class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    student_id = models.CharField(max_length=50)
    student_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    present_start = models.BooleanField(default=False)
    present_end = models.BooleanField(default=False)
    recorded_at = models.DateTimeField(auto_now_add=True)
    # Student can select multiple sections they belong to
    sections = models.ManyToManyField(EventSection, blank=True, related_name='attendees')

    class Meta:
        # Ensure each student can register only once per event and each code is unique per event
        unique_together = (('event', 'student_id'), ('event', 'code'))

    def __str__(self):
        return f"{self.student_name} - {self.event.title}"
