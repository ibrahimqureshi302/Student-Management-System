from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)
    # code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=100)
    credit_hours = models.IntegerField(default=3)
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class Section(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='sections')
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    section_name = models.CharField(max_length=1)
    class_teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
    capacity = models.IntegerField(default=30)
    room_number = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=9)

    def __str__(self):
        return f"{self.department.name} - Sem {self.semester} - Sec {self.section_name}"


class Enrollment(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course', 'section')

    def __str__(self):
        return f"{self.student} -> {self.course}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('leave', 'Leave'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendances')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    marked_by = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course', 'date')

    def __str__(self):
        return f"{self.student} - {self.course} - {self.date}: {self.status}"


class Marks(models.Model):
    MAX_QUIZ = 25
    MAX_ASSIGNMENT = 25
    MAX_MID = 100
    MAX_FINAL = 100
    MAX_TOTAL = MAX_QUIZ + MAX_ASSIGNMENT + MAX_MID + MAX_FINAL  # 250

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='marks')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='marks')
    quiz_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_QUIZ)],
    )
    assignment_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_ASSIGNMENT)],
    )
    mid_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_MID)],
    )
    final_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_FINAL)],
    )
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade = models.CharField(max_length=2, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    semester = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course', 'semester')

    def save(self, *args, **kwargs):
        self.total_marks = (
            (self.quiz_marks or 0)
            + (self.assignment_marks or 0)
            + (self.mid_marks or 0)
            + (self.final_marks or 0)
        )
        pct = (float(self.total_marks) / float(self.MAX_TOTAL)) * 100 if self.MAX_TOTAL else 0
        self.percentage = round(pct, 2)
        if pct >= 85:
            self.grade, self.gpa = 'A', 4.00
        elif pct >= 80:
            self.grade, self.gpa = 'A-', 3.70
        elif pct >= 75:
            self.grade, self.gpa = 'B+', 3.30
        elif pct >= 70:
            self.grade, self.gpa = 'B', 3.00
        elif pct >= 65:
            self.grade, self.gpa = 'B-', 2.70
        elif pct >= 60:
            self.grade, self.gpa = 'C+', 2.30
        elif pct >= 55:
            self.grade, self.gpa = 'C', 2.00
        elif pct >= 50:
            self.grade, self.gpa = 'D', 1.00
        else:
            self.grade, self.gpa = 'F', 0.00
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.course}: {self.total_marks}/{self.MAX_TOTAL} ({self.grade})"
