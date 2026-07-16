from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_fees, name='fees'),
    path('create/', views.create_fee, name='create_fee'),
    path('report/due/', views.due_fees_report, name='due_fees_report'),
    path('student/<int:id>/', views.student_fees, name='student_fees'),
    path('<int:id>/', views.get_fee, name='fee_detail'),
    path('<int:id>/update/', views.update_fee, name='update_fee'),
    path('<int:id>/delete/', views.delete_fee, name='delete_fee'),
    path('<int:id>/pay/', views.pay_fee, name='pay_fee'),
]
