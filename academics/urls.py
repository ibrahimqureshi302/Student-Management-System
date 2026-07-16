from django.urls import path
from . import views

urlpatterns = [
    path('', views.departments_list, name='departments'),
    path('<int:id>/', views.department_detail, name='department_detail'),

    path('courses/', views.courses_list, name='courses'),
    path('courses/<int:id>/', views.course_detail, name='course_detail'),

    path('sections/', views.sections_list, name='sections'),
    path('sections/<int:id>/', views.section_detail, name='section_detail'),

    path('enrollments/', views.enrollments_list, name='enrollments'),
    path('enrollments/<int:id>/', views.enrollment_detail, name='enrollment_detail'),

    path('attendance/', views.attendance_list, name='attendance'),
    path('attendance/<int:id>/', views.attendance_delete, name='attendance_delete'),

    path('marks/', views.marks_list, name='marks'),
    path('marks/<int:id>/', views.marks_detail, name='marks_detail'),
]
