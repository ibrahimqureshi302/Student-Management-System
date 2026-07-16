from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notifications/', views.get_notifications, name='notifications'),
    path('notifications/<int:id>/read/', views.mark_notification_read, name='notification_read'),
    path('notifications/send/', views.send_notification, name='send_notification'),
]
