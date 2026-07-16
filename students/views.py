from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Count

from accounts.models import User
from .models import Student
from .serializers import StudentSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_students(request):
    students = Student.objects.select_related('user', 'department', 'section').all()
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student(request, id):
    try:
        student = Student.objects.select_related('user', 'department', 'section').get(id=id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(StudentSerializer(student).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_student(request):
    if request.user.role not in ['super_admin', 'admin']:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    data = request.data.copy()
    user_id = data.get('user_id') or data.get('user')

    # Auto-create user if user credentials are provided instead of user_id
    if not user_id:
        email = data.get('email')
        password = data.get('password', 'student123')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone = data.get('phone', '')

        if not email or not first_name or not last_name:
            return Response(
                {'error': 'Provide user_id OR (email, first_name, last_name) to create a new user.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(email=email).exists():
            return Response({'error': 'A user with this email already exists'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(
            email=email, password=password,
            first_name=first_name, last_name=last_name,
            phone=phone, role='student',
        )
    else:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if Student.objects.filter(user=user).exists():
            return Response({'error': 'Student profile already exists for this user'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        student = Student.objects.create(
            user=user,
            registration_no=data.get('registration_no'),
            # roll_number=data.get('roll_number'),
            father_name=data.get('father_name'),
            cnic=data.get('cnic') or None,
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender', 'M'),
            address=data.get('address', ''),
            guardian_contact=data.get('guardian_contact', ''),
            batch=data.get('batch'),
            current_semester=data.get('current_semester', 1),
            department_id=data.get('department') or None,
            section_id=data.get('section') or None,
            status=data.get('status', 'active'),
        )
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_student(request, id):
    if request.user.role not in ['super_admin', 'admin']:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        student = Student.objects.get(id=id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    editable = ['registration_no', 'father_name', 'cnic', 'date_of_birth',
                'gender', 'address', 'guardian_contact', 'batch', 'current_semester', 'status']
    for field in editable:
        if field in request.data:
            setattr(student, field, request.data.get(field))
    if 'department' in request.data:
        student.department_id = request.data.get('department') or None
    if 'section' in request.data:
        student.section_id = request.data.get('section') or None
    student.save()
    return Response(StudentSerializer(student).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_student(request, id):
    if request.user.role not in ['super_admin', 'admin']:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        student = Student.objects.get(id=id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    student.delete()
    return Response({'message': 'Student deleted'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    from fees.models import Fee
    from academics.models import Marks, Attendance

    if request.user.role != 'student':
        return Response({'error': 'Only students can access this endpoint'},
                        status=status.HTTP_403_FORBIDDEN)
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

    fees = Fee.objects.filter(student=student)
    total_amount = sum(float(f.amount) for f in fees)
    paid_amount = sum(float(f.paid_amount) for f in fees)

    attendance = Attendance.objects.filter(student=student)
    attendance_total = attendance.count()
    attendance_present = attendance.filter(status='present').count()
    attendance_percentage = (attendance_present / attendance_total * 100) if attendance_total else 0

    avg_gpa = Marks.objects.filter(student=student).aggregate(avg=Avg('gpa'))['avg'] or 0

    return Response({
        'student': StudentSerializer(student).data,
        'fees': {'total': total_amount, 'paid': paid_amount, 'due': total_amount - paid_amount},
        'attendance': {'total': attendance_total, 'present': attendance_present,
                       'percentage': round(attendance_percentage, 2)},
        'average_gpa': round(float(avg_gpa), 2),
    })
