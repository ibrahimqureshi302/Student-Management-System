from django.db import models
from accounts.models import User
from students.models import Student

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    occupation = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    children = models.ManyToManyField(Student, through='StudentParent')
    
    def __str__(self):
        return self.user.full_name

class StudentParent(models.Model):
    RELATION_CHOICES = [('father', 'Father'), ('mother', 'Mother'), ('guardian', 'Guardian')]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    relationship = models.CharField(max_length=10, choices=RELATION_CHOICES)