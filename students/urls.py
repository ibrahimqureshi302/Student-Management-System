from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_students, name='students'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('create/', views.create_student, name='create_student'),
    path('<int:id>/', views.get_student, name='student_detail'),
    path('<int:id>/update/', views.update_student, name='update_student'),
    path('<int:id>/delete/', views.delete_student, name='delete_student'),
]
