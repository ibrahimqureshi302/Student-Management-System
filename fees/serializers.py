from decimal import Decimal, InvalidOperation

from rest_framework import serializers
from .models import Fee


class FeeSerializer(serializers.ModelSerializer):
    remaining_amount = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    registration_no = serializers.SerializerMethodField()

    class Meta:
        model = Fee
        fields = ['id', 'student', 'student_name', 'registration_no', 'amount', 'paid_amount',
                  'remaining_amount', 'due_date', 'status', 'payment_date']

    def get_remaining_amount(self, obj):
        def _d(v):
            if isinstance(v, Decimal):
                return v
            try:
                return Decimal(str(v or 0))
            except (InvalidOperation, ValueError):
                return Decimal('0')
        return str(_d(obj.amount) - _d(obj.paid_amount))

    def get_student_name(self, obj):
        try:
            return obj.student.user.full_name if obj.student and obj.student.user else "N/A"
        except Exception:
            return "N/A"

    def get_registration_no(self, obj):
        try:
            return obj.student.registration_no if obj.student else None
        except Exception:
            return None
