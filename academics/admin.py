from django.contrib import admin
from .models import Department, Course, Section, Enrollment, Attendance, Marks


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_code', 'course_name', 'department', 'credit_hours', 'semester', 'is_active')
    list_filter = ('department', 'semester', 'is_active')
    search_fields = ('course_code', 'course_name')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'section_name', 'department', 'semester', 'class_teacher', 'capacity', 'room_number')
    list_filter = ('department', 'semester')
    search_fields = ('section_name', 'room_number')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course', 'section', 'enrolled_at')
    list_filter = ('course', 'section')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course', 'date', 'status')
    list_filter = ('status', 'date', 'course')


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course', 'total_marks', 'grade', 'gpa', 'semester')
    list_filter = ('grade', 'semester', 'course')
