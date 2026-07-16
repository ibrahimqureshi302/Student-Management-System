from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/students/', include('students.urls')),
    path('api/teachers/', include('teachers.urls')),
    path('api/departments/', include('academics.urls')),
    path('api/fees/', include('fees.urls')),
    path('api/parents/', include('parents.urls')),
    path('api/', include('core.urls')),
]
