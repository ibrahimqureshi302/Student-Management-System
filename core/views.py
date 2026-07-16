from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count

from accounts.models import User
from students.models import Student
from teachers.models import Teacher
from academics.models import Department, Course, Section
from fees.models import Fee
from parents.models import Parent

from .models import Notification
from .serializers import NotificationSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    user = request.user
    role = user.role
    data = {'role': role}

    if role in ['super_admin', 'admin']:
        total_amount = Fee.objects.aggregate(total=Sum('amount'))['total'] or 0
        paid_amount = Fee.objects.aggregate(total=Sum('paid_amount'))['total'] or 0
        data.update({
            'total_students': Student.objects.count(),
            'total_teachers': Teacher.objects.count(),
            'total_parents': Parent.objects.count(),
            'total_departments': Department.objects.count(),
            'total_courses': Course.objects.count(),
            'total_sections': Section.objects.count(),
            'total_fees_amount': float(total_amount),
            'total_fees_paid': float(paid_amount),
            'total_fees_due': float(total_amount) - float(paid_amount),
        })
    elif role == 'teacher':
        try:
            teacher = user.teacher_profile
            data.update({
                'employee_id': teacher.employee_id,
                'designation': teacher.designation,
                'department': teacher.department.name if teacher.department else None,
                'courses_count': Course.objects.filter(teacher=teacher).count(),
                'sections_count': Section.objects.filter(class_teacher=teacher).count(),
            })
        except Teacher.DoesNotExist:
            data['message'] = 'Teacher profile not found'
    elif role == 'student':
        try:
            student = user.student_profile
            fees = Fee.objects.filter(student=student)
            total = sum(float(f.amount) for f in fees)
            paid = sum(float(f.paid_amount) for f in fees)
            data.update({
                'registration_no': student.registration_no,
                # 'roll_number': student.roll_number,
                'batch': student.batch,
                'current_semester': student.current_semester,
                'department': student.department.name if student.department else None,
                'section': str(student.section) if student.section else None,
                'total_fees': total,
                'paid_fees': paid,
                'due_fees': total - paid,
            })
        except Student.DoesNotExist:
            data['message'] = 'Student profile not found'
    elif role == 'parent':
        try:
            parent = user.parent_profile
            data.update({
                'occupation': parent.occupation,
                'phone': parent.phone,
                'children_count': parent.children.count(),
            })
        except Parent.DoesNotExist:
            data['message'] = 'Parent profile not found'

    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    return Response(NotificationSerializer(notifications, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, id):
    try:
        notification = Notification.objects.get(id=id, user=request.user)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    notification.is_read = True
    notification.save()
    return Response(NotificationSerializer(notification).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_notification(request):
    if request.user.role not in ['super_admin', 'admin']:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get('user_id')
    title = request.data.get('title')
    message = request.data.get('message')
    notification_type = request.data.get('notification_type', 'info')

    if not user_id or not title or not message:
        return Response({'error': 'user_id, title and message are required'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        target = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    notification = Notification.objects.create(
        user=target, title=title, message=message, notification_type=notification_type
    )
    return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)
