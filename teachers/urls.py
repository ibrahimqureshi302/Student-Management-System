from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_teachers, name='teachers'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('create/', views.create_teacher, name='create_teacher'),
    path('<int:id>/', views.get_teacher, name='teacher_detail'),
    path('<int:id>/update/', views.update_teacher, name='update_teacher'),
    path('<int:id>/delete/', views.delete_teacher, name='delete_teacher'),
]
