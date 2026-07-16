from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg

from accounts.models import User
from students.models import Student
from students.serializers import StudentSerializer
from .models import Parent, StudentParent
from .serializers import ParentSerializer, StudentParentSerializer


def _is_admin(user):
    return user.role in ['super_admin', 'admin']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_parents(request):
    parents = Parent.objects.select_related('user').all()
    return Response(ParentSerializer(parents, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_parent(request, id):
    try:
        parent = Parent.objects.select_related('user').get(id=id)
    except Parent.DoesNotExist:
        return Response({'error': 'Parent not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(ParentSerializer(parent).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_parent(request):
    if not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    user_id = data.get('user_id') or data.get('user')

    if not user_id:
        email = data.get('email')
        password = data.get('password', 'parent123')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone = data.get('phone', '')
        if not email or not first_name or not last_name:
            return Response({'error': 'Provide user_id OR email/first_name/last_name.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'A user with this email already exists'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(
            email=email, password=password,
            first_name=first_name, last_name=last_name,
            phone=phone, role='parent',
        )
    else:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if Parent.objects.filter(user=user).exists():
            return Response({'error': 'Parent profile already exists for this user'},
                            status=status.HTTP_400_BAD_REQUEST)

    parent = Parent.objects.create(
        user=user,
        occupation=data.get('occupation', ''),
        phone=data.get('phone', ''),
    )
    return Response(ParentSerializer(parent).data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_parent(request, id):
    if not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        parent = Parent.objects.get(id=id)
    except Parent.DoesNotExist:
        return Response({'error': 'Parent not found'}, status=status.HTTP_404_NOT_FOUND)

    for field in ['occupation', 'phone']:
        if field in request.data:
            setattr(parent, field, request.data.get(field))
    parent.save()
    return Response(ParentSerializer(parent).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_parent(request, id):
    if not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        parent = Parent.objects.get(id=id)
    except Parent.DoesNotExist:
        return Response({'error': 'Parent not found'}, status=status.HTTP_404_NOT_FOUND)
    parent.delete()
    return Response({'message': 'Parent deleted'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_children(request):
    if request.user.role != 'parent':
        return Response({'error': 'Only parents can access this endpoint'},
                        status=status.HTTP_403_FORBIDDEN)
    try:
        parent = request.user.parent_profile
    except Parent.DoesNotExist:
        return Response({'error': 'Parent profile not found'}, status=status.HTTP_404_NOT_FOUND)

    children = parent.children.select_related('user', 'department', 'section').all()
    return Response(StudentSerializer(children, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def link_student(request, id):
    if not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        parent = Parent.objects.get(id=id)
    except Parent.DoesNotExist:
        return Response({'error': 'Parent not found'}, status=status.HTTP_404_NOT_FOUND)

    student_id = request.data.get('student_id') or request.data.get('student')
    relationship = request.data.get('relationship', 'guardian')

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    link, created = StudentParent.objects.get_or_create(
        parent=parent, student=student,
        defaults={'relationship': relationship},
    )
    if not created:
        link.relationship = relationship
        link.save()
    return Response(StudentParentSerializer(link).data,
                    status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def child_progress(request, id):
    from fees.models import Fee
    from fees.serializers import FeeSerializer
    from academics.models import Marks, Attendance
    from academics.serializers import MarksSerializer, AttendanceSerializer

    try:
        student = Student.objects.select_related('user').get(id=id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    # Parents can only see their own children
    if request.user.role == 'parent':
        try:
            parent = request.user.parent_profile
            if not parent.children.filter(id=student.id).exists():
                return Response({'error': 'This child is not linked to your account'},
                                status=status.HTTP_403_FORBIDDEN)
        except Parent.DoesNotExist:
            return Response({'error': 'Parent profile not found'}, status=status.HTTP_404_NOT_FOUND)
    elif not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    fees = Fee.objects.filter(student=student)
    marks = Marks.objects.filter(student=student)
    attendance = Attendance.objects.filter(student=student)

    total_attendance = attendance.count()
    present_attendance = attendance.filter(status='present').count()
    attendance_percentage = (present_attendance / total_attendance * 100) if total_attendance else 0

    total_fees = sum(float(f.amount) for f in fees)
    paid_fees = sum(float(f.paid_amount) for f in fees)
    avg_gpa = marks.aggregate(avg=Avg('gpa'))['avg'] or 0

    return Response({
        'student': StudentSerializer(student).data,
        'fees': {'total': total_fees, 'paid': paid_fees, 'due': total_fees - paid_fees,
                 'records': FeeSerializer(fees, many=True).data},
        'marks': MarksSerializer(marks, many=True).data,
        'average_gpa': round(float(avg_gpa), 2),
        'attendance': {
            'total': total_attendance,
            'present': present_attendance,
            'percentage': round(attendance_percentage, 2),
            'records': AttendanceSerializer(attendance, many=True).data,
        },
    })
