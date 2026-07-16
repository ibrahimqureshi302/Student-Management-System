from rest_framework import serializers
from .models import Department, Course, Section, Enrollment, Attendance, Marks


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'department', 'department_name', 'course_code', 'course_name',
                  'credit_hours', 'semester', 'teacher', 'teacher_name', 'is_active']

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_teacher_name(self, obj):
        return obj.teacher.user.full_name if obj.teacher and obj.teacher.user else None


class SectionSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    class_teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ['id', 'department', 'department_name', 'semester', 'section_name',
                  'class_teacher', 'class_teacher_name', 'capacity', 'room_number', 'academic_year']

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_class_teacher_name(self, obj):
        return obj.class_teacher.user.full_name if obj.class_teacher and obj.class_teacher.user else None


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    course_name = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_name', 'course', 'course_name', 'section', 'enrolled_at']

    def get_student_name(self, obj):
        return obj.student.user.full_name if obj.student and obj.student.user else None

    def get_course_name(self, obj):
        return obj.course.course_name if obj.course else None


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    registration_no = serializers.SerializerMethodField()
    course_name = serializers.SerializerMethodField()
    course_code = serializers.SerializerMethodField()
    marked_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'registration_no',
                  'course', 'course_name', 'course_code',
                  'date', 'status', 'marked_by', 'marked_by_name']

    def get_student_name(self, obj):
        return obj.student.user.full_name if obj.student and obj.student.user else None

    def get_registration_no(self, obj):
        return obj.student.registration_no if obj.student else None

    def get_course_name(self, obj):
        return obj.course.course_name if obj.course else None

    def get_course_code(self, obj):
        return obj.course.course_code if obj.course else None

    def get_marked_by_name(self, obj):
        return obj.marked_by.user.full_name if obj.marked_by and obj.marked_by.user else None


class MarksSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    course_name = serializers.SerializerMethodField()
    course_code = serializers.SerializerMethodField()
    registration_no = serializers.SerializerMethodField()

    class Meta:
        model = Marks
        fields = [
            'id', 'student', 'student_name', 'registration_no',
            'course', 'course_name', 'course_code',
            'quiz_marks', 'assignment_marks', 'mid_marks', 'final_marks',
            'total_marks', 'percentage', 'grade', 'gpa', 'semester', 'updated_at',
        ]
        read_only_fields = ['total_marks', 'percentage', 'grade', 'gpa', 'updated_at']

    def get_student_name(self, obj):
        return obj.student.user.full_name if obj.student and obj.student.user else None

    def get_registration_no(self, obj):
        return obj.student.registration_no if obj.student else None

    def get_course_name(self, obj):
        return obj.course.course_name if obj.course else None

    def get_course_code(self, obj):
        return obj.course.course_code if obj.course else None
