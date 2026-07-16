from django.contrib import admin
from .models import Teacher

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee_id', 'full_name', 'designation', 'department', 'status', 'joining_date')
    list_filter = ('designation', 'status', 'department', 'joining_date')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'specialization')
    
    def full_name(self, obj):
        return obj.user.full_name
    full_name.short_description = 'Teacher Name'

admin.site.register(Teacher, TeacherAdmin)