from rest_framework import serializers
from .models import Parent, StudentParent


class ParentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Parent
        fields = ['id', 'user', 'full_name', 'email', 'occupation', 'phone', 'children_count']

    def get_full_name(self, obj):
        try:
            return obj.user.full_name if obj.user else "N/A"
        except Exception:
            return "N/A"

    def get_email(self, obj):
        try:
            return obj.user.email if obj.user else "N/A"
        except Exception:
            return "N/A"

    def get_children_count(self, obj):
        return obj.children.count()


class StudentParentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentParent
        fields = ['id', 'student', 'student_name', 'parent', 'parent_name', 'relationship']

    def get_student_name(self, obj):
        try:
            return obj.student.user.full_name if obj.student and obj.student.user else None
        except Exception:
            return None

    def get_parent_name(self, obj):
        try:
            return obj.parent.user.full_name if obj.parent and obj.parent.user else None
        except Exception:
            return None
