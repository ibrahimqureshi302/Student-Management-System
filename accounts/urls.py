from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.get_profile, name='profile'),
    path('users/', views.get_users, name='users'),

    # Super-admin-only admin management
    path('admins/', views.admins_list, name='admins'),
    path('admins/<int:id>/', views.admin_detail, name='admin_detail'),
]
