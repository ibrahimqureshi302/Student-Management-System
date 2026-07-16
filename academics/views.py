from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Department, Course, Section, Enrollment, Attendance, Marks
from .serializers import (
    DepartmentSerializer, CourseSerializer, SectionSerializer, EnrollmentSerializer,
    AttendanceSerializer, MarksSerializer,
)


def _is_admin(user):
    return user.role in ['super_admin', 'admin']


def _is_faculty(user):
    return user.role in ['super_admin', 'admin', 'teacher']


# ----------------- Department -----------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def departments_list(request):
    if request.method == 'GET':
        departments = Department.objects.all()
        return Response(DepartmentSerializer(departments, many=True).data)

    if not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    serializer = DepartmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def department_detail(request, id):
    try:
        department = Department.objects.get(id=id)
    except Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(DepartmentSerializer(department).data)

    if not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    if request.method in ['PUT', 'PATCH']:
        serializer = DepartmentSerializer(department, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    department.delete()
    return Response({'message': 'Department deleted'}, status=status.HTTP_204_NO_CONTENT)


# ----------------- Course -----------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def courses_list(request):
    if request.method == 'GET':
        courses = Course.objects.select_related('department', 'teacher', 'teacher__user').all()
        return Response(CourseSerializer(courses, many=True).data)

    if not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    serializer = CourseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def course_detail(request, id):
    try:
        course = Course.objects.get(id=id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(CourseSerializer(course).data)

    if not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    if request.method in ['PUT', 'PATCH']:
        serializer = CourseSerializer(course, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    course.delete()
    return Response({'message': 'Course deleted'}, status=status.HTTP_204_NO_CONTENT)


# ----------------- Section -----------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def sections_list(request):
    if request.method == 'GET':
        sections = Section.objects.select_related('department', 'class_teacher', 'class_teacher__user').all()
        return Response(SectionSerializer(sections, many=True).data)

    if not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    serializer = SectionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def section_detail(request, id):
    try:
        section = Section.objects.get(id=id)
    except Section.DoesNotExist:
        return Response({'error': 'Section not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(SectionSerializer(section).data)

    if not _is_admin(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    if request.method in ['PUT', 'PATCH']:
        serializer = SectionSerializer(section, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    section.delete()
    return Response({'message': 'Section deleted'}, status=status.HTTP_204_NO_CONTENT)


# ----------------- Enrollment (admin/super_admin only) -----------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def enrollments_list(request):
    if request.method == 'GET':
        qs = Enrollment.objects.select_related(
            'student', 'student__user', 'course', 'section', 'section__department'
        )
        course_id = request.query_params.get('course')
        section_id = request.query_params.get('section')
        student_id = request.query_params.get('student')
        if course_id:
            qs = qs.filter(course_id=course_id)
        if section_id:
            qs = qs.filter(section_id=section_id)
        if student_id:
            qs = qs.filter(student_id=student_id)
        return Response(EnrollmentSerializer(qs, many=True).data)

    if not _is_admin(request.user):
        return Response({'error': 'Only admins can allocate courses'},
                        status=status.HTTP_403_FORBIDDEN)

    student_id = request.data.get('student')
    course_id = request.data.get('course')
    section_id = request.data.get('section')

    if not student_id or not course_id or not section_id:
        return Response({'error': 'student, course, and section are required'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        section = Section.objects.get(id=section_id)
    except Section.DoesNotExist:
        return Response({'error': 'Section not found'}, status=status.HTTP_404_NOT_FOUND)

    if Enrollment.objects.filter(student_id=student_id, course_id=course_id, section_id=section_id).exists():
        return Response({'error': 'Student is already enrolled in this course/section'},
                        status=status.HTTP_400_BAD_REQUEST)

    distinct_students = Enrollment.objects.filter(section=section).values_list('student', flat=True).distinct().count()
    is_new_student_in_section = not Enrollment.objects.filter(section=section, student_id=student_id).exists()
    if is_new_student_in_section and distinct_students >= section.capacity:
        return Response({'error': f'Section is at full capacity ({section.capacity} students)'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        enrollment = Enrollment.objects.create(
            student_id=student_id, course_id=course_id, section_id=section_id,
        )
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def enrollment_detail(request, id):
    try:
        enrollment = Enrollment.objects.select_related(
            'student', 'student__user', 'course', 'section'
        ).get(id=id)
    except Enrollment.DoesNotExist:
        return Response({'error': 'Enrollment not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(EnrollmentSerializer(enrollment).data)

    if not _is_admin(request.user):
        return Response({'error': 'Only admins can remove enrollments'},
                        status=status.HTTP_403_FORBIDDEN)
    enrollment.delete()
    return Response({'message': 'Enrollment removed'}, status=status.HTTP_204_NO_CONTENT)


# ----------------- Attendance (teachers + admins) -----------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def attendance_list(request):
    if request.method == 'GET':
        qs = Attendance.objects.select_related(
            'student', 'student__user', 'course', 'marked_by', 'marked_by__user'
        )
        for key, field in (('course', 'course_id'), ('student', 'student_id'), ('date', 'date')):
            val = request.query_params.get(key)
            if val:
                qs = qs.filter(**{field: val})
        return Response(AttendanceSerializer(qs.order_by('-date'), many=True).data)

    if not _is_faculty(request.user):
        return Response({'error': 'Only teachers and admins can mark attendance'},
                        status=status.HTTP_403_FORBIDDEN)

    marked_by = None
    if request.user.role == 'teacher':
        try:
            marked_by = request.user.teacher_profile
        except Exception:
            pass

    # Bulk mode: {course, date, records: [{student, status}, ...]}
    if isinstance(request.data.get('records'), list):
        course_id = request.data.get('course')
        date = request.data.get('date')
        if not course_id or not date:
            return Response({'error': 'course and date are required for bulk attendance'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not Course.objects.filter(id=course_id).exists():
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        results = []
        for r in request.data['records']:
            student_id = r.get('student')
            st = r.get('status', 'present')
            if not student_id:
                continue
            att, _ = Attendance.objects.update_or_create(
                student_id=student_id, course_id=course_id, date=date,
                defaults={'status': st, 'marked_by': marked_by},
            )
            results.append(att)
        return Response(AttendanceSerializer(results, many=True).data,
                        status=status.HTTP_201_CREATED)

    # Single record create / upsert
    student_id = request.data.get('student')
    course_id = request.data.get('course')
    date = request.data.get('date')
    st = request.data.get('status', 'present')

    if not student_id or not course_id or not date:
        return Response({'error': 'student, course, and date are required'},
                        status=status.HTTP_400_BAD_REQUEST)

    att, _ = Attendance.objects.update_or_create(
        student_id=student_id, course_id=course_id, date=date,
        defaults={'status': st, 'marked_by': marked_by},
    )
    return Response(AttendanceSerializer(att).data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def attendance_delete(request, id):
    if not _is_faculty(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        att = Attendance.objects.get(id=id)
    except Attendance.DoesNotExist:
        return Response({'error': 'Attendance record not found'}, status=status.HTTP_404_NOT_FOUND)
    att.delete()
    return Response({'message': 'Attendance deleted'}, status=status.HTTP_204_NO_CONTENT)


# ----------------- Marks (teachers + admins) -----------------

def _clamp(val, lo, hi):
    try:
        v = float(val)
    except (TypeError, ValueError):
        return None
    return max(lo, min(hi, v))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def marks_list(request):
    if request.method == 'GET':
        qs = Marks.objects.select_related(
            'student', 'student__user', 'course'
        )
        for key, field in (('course', 'course_id'), ('student', 'student_id'),
                           ('semester', 'semester')):
            val = request.query_params.get(key)
            if val:
                qs = qs.filter(**{field: val})
        return Response(MarksSerializer(qs.order_by('-updated_at'), many=True).data)

    if not _is_faculty(request.user):
        return Response({'error': 'Only teachers and admins can record marks'},
                        status=status.HTTP_403_FORBIDDEN)

    data = request.data
    student_id = data.get('student')
    course_id = data.get('course')
    semester = data.get('semester')

    if not student_id or not course_id:
        return Response({'error': 'student and course are required'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    if not semester:
        semester = course.semester

    quiz = _clamp(data.get('quiz_marks', 0), 0, Marks.MAX_QUIZ)
    assignment = _clamp(data.get('assignment_marks', 0), 0, Marks.MAX_ASSIGNMENT)
    mid = _clamp(data.get('mid_marks', 0), 0, Marks.MAX_MID)
    final = _clamp(data.get('final_marks', 0), 0, Marks.MAX_FINAL)

    if None in (quiz, assignment, mid, final):
        return Response({'error': 'Invalid marks — must be numeric'},
                        status=status.HTTP_400_BAD_REQUEST)

    marks, _ = Marks.objects.update_or_create(
        student_id=student_id, course_id=course_id, semester=semester,
        defaults={
            'quiz_marks': quiz,
            'assignment_marks': assignment,
            'mid_marks': mid,
            'final_marks': final,
        },
    )
    return Response(MarksSerializer(marks).data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def marks_detail(request, id):
    try:
        marks = Marks.objects.select_related('student', 'student__user', 'course').get(id=id)
    except Marks.DoesNotExist:
        return Response({'error': 'Marks record not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(MarksSerializer(marks).data)

    if not _is_faculty(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    if request.method in ['PUT', 'PATCH']:
        mapping = [
            ('quiz_marks', 0, Marks.MAX_QUIZ),
            ('assignment_marks', 0, Marks.MAX_ASSIGNMENT),
            ('mid_marks', 0, Marks.MAX_MID),
            ('final_marks', 0, Marks.MAX_FINAL),
        ]
        for field, lo, hi in mapping:
            if field in request.data:
                val = _clamp(request.data.get(field), lo, hi)
                if val is None:
                    return Response({'error': f'Invalid {field}'}, status=status.HTTP_400_BAD_REQUEST)
                setattr(marks, field, val)
        if 'semester' in request.data:
            marks.semester = request.data.get('semester')
        marks.save()
        return Response(MarksSerializer(marks).data)

    marks.delete()
    return Response({'message': 'Marks deleted'}, status=status.HTTP_204_NO_CONTENT)
