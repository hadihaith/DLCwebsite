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

