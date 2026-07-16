from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    section_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'user', 'full_name', 'email', 'registration_no',
            'father_name', 'cnic', 'date_of_birth', 'gender', 'address',
            'guardian_contact', 'batch', 'current_semester', 'department',
            'department_name', 'section', 'section_name', 'status', 'created_at'
        ]
    
    def get_full_name(self, obj):
        try:
            return obj.user.full_name if obj.user else "N/A"
        except:
            return "User deleted"
    
    def get_email(self, obj):
        try:
            return obj.user.email if obj.user else "N/A"
        except:
            return "N/A"
    
    def get_department_name(self, obj):
        try:
            return obj.department.name if obj.department else "Not Assigned"
        except:
            return "N/A"
    
    def get_section_name(self, obj):
        try:
            return obj.section.section_name if obj.section else "Not Assigned"
        except:
            return "N/A"