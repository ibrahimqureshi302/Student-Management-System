from datetime import date
from decimal import Decimal

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from students.models import Student
from .models import Fee
from .serializers import FeeSerializer


def _is_admin(user):
    return user.role in ['super_admin', 'admin']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_fees(request):
    fees = Fee.objects.select_related('student', 'student__user').all()
    return Response(FeeSerializer(fees, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_fee(request, id):
    try:
        fee = Fee.objects.select_related('student', 'student__user').get(id=id)
    except Fee.DoesNotExist:
        return Response({'error': 'Fee record not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(FeeSerializer(fee).data)


def _to_decimal(value, default='0'):
    if value is None or value == '':
        return Decimal(default)
    try:
        return Decimal(str(value))
    except Exception:
        return None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_fee(request):
    if not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    student_id = request.data.get('student')
    if not student_id:
        return Response({'error': 'Student is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    if Fee.objects.filter(student=student).exists():
        return Response({'error': 'A fee is already assigned to this student'},
                        status=status.HTTP_400_BAD_REQUEST)

    amount = _to_decimal(request.data.get('amount'))
    paid_amount = _to_decimal(request.data.get('paid_amount', 0))
    if amount is None or paid_amount is None:
        return Response({'error': 'Invalid amount — must be numeric'},
                        status=status.HTTP_400_BAD_REQUEST)
    if amount <= 0:
        return Response({'error': 'Amount must be greater than zero'},
                        status=status.HTTP_400_BAD_REQUEST)

    due_date = request.data.get('due_date')
    if not due_date:
        return Response({'error': 'Due date is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        fee = Fee.objects.create(
            student=student,
            amount=amount,
            paid_amount=paid_amount,
            due_date=due_date,
            status=request.data.get('status', 'unpaid'),
        )
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    fee.refresh_from_db()
    return Response(FeeSerializer(fee).data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_fee(request, id):
    if not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        fee = Fee.objects.get(id=id)
    except Fee.DoesNotExist:
        return Response({'error': 'Fee record not found'}, status=status.HTTP_404_NOT_FOUND)

    for field in ('amount', 'paid_amount'):
        if field in request.data:
            val = _to_decimal(request.data.get(field))
            if val is None:
                return Response({'error': f'Invalid {field}'}, status=status.HTTP_400_BAD_REQUEST)
            setattr(fee, field, val)
    for field in ('due_date', 'status', 'payment_date'):
        if field in request.data:
            setattr(fee, field, request.data.get(field))
    fee.save()
    fee.refresh_from_db()
    return Response(FeeSerializer(fee).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_fee(request, id):
    if not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        fee = Fee.objects.get(id=id)
    except Fee.DoesNotExist:
        return Response({'error': 'Fee record not found'}, status=status.HTTP_404_NOT_FOUND)
    fee.delete()
    return Response({'message': 'Fee deleted'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pay_fee(request, id):
    try:
        fee = Fee.objects.get(id=id)
    except Fee.DoesNotExist:
        return Response({'error': 'Fee record not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        amount = Decimal(str(request.data.get('amount', 0)))
    except Exception:
        return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

    if amount <= 0:
        return Response({'error': 'Payment amount must be greater than zero'},
                        status=status.HTTP_400_BAD_REQUEST)

    fee.paid_amount = (fee.paid_amount or Decimal('0')) + amount
    if fee.paid_amount >= fee.amount:
        fee.paid_amount = fee.amount
        fee.status = 'paid'
        fee.payment_date = date.today()
    elif fee.paid_amount > 0:
        fee.status = 'partial'
    fee.save()
    return Response(FeeSerializer(fee).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_fees(request, id):
    fees = Fee.objects.filter(student_id=id).select_related('student', 'student__user')
    total = sum(float(f.amount) for f in fees)
    paid = sum(float(f.paid_amount) for f in fees)
    return Response({
        'total': total,
        'paid': paid,
        'due': total - paid,
        'fees': FeeSerializer(fees, many=True).data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def due_fees_report(request):
    if not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    fees = Fee.objects.exclude(status='paid').select_related('student', 'student__user')
    return Response(FeeSerializer(fees, many=True).data)
