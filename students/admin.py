from django.contrib import admin
from .models import Student

class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'registration_no', 'full_name', 'batch', 'current_semester', 'status')
    list_filter = ('status', 'batch', 'current_semester', 'gender')
    search_fields = ('registration_no', 'roll_number', 'user__first_name', 'user__last_name', 'father_name')
    
    def full_name(self, obj):
        return obj.user.full_name
    full_name.short_description = 'Student Name'

admin.site.register(Student, StudentAdmin)