from django.db import models
from accounts.models import User

class Student(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('alumni', 'Alumni')]
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    registration_no = models.CharField(max_length=20, unique=True)
    # roll_number = models.CharField(max_length=20, unique=True)
    father_name = models.CharField(max_length=100)
    cnic = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    guardian_contact = models.CharField(max_length=15)
    batch = models.IntegerField()
    current_semester = models.IntegerField(default=1)
    department = models.ForeignKey('academics.Department', on_delete=models.SET_NULL, null=True)
    section = models.ForeignKey('academics.Section', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.full_name} - {self.registration_no}"
    
    @property
    def full_name(self):
        return self.user.full_name