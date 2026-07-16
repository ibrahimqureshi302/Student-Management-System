from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_parents, name='parents'),
    path('children/', views.get_children, name='parent_children'),
    path('create/', views.create_parent, name='create_parent'),
    path('child/<int:id>/progress/', views.child_progress, name='child_progress'),
    path('<int:id>/', views.get_parent, name='parent_detail'),
    path('<int:id>/update/', views.update_parent, name='update_parent'),
    path('<int:id>/delete/', views.delete_parent, name='delete_parent'),
    path('<int:id>/link-student/', views.link_student, name='link_student'),
]
