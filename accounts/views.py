from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    role = request.data.get('role', 'student')
    
    # Validate required fields
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not password:
        return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not first_name:
        return Response({'error': 'First name is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not last_name:
        return Response({'error': 'Last name is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate email format
    if '@' not in email or '.' not in email:
        return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate password strength
    if len(password) < 6:
        return Response({'error': 'Password must be at least 6 characters'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate role
    valid_roles = ['super_admin', 'admin', 'teacher', 'student', 'parent']
    if role not in valid_roles:
        return Response({'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Create user
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=role
    )
    
    return Response({
        'message': 'User created successfully',
        'user': UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(email=email, password=password)
    
    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({'error': 'Account disabled'}, status=status.HTTP_401_UNAUTHORIZED)
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    if request.user.role not in ['super_admin', 'admin']:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    users = User.objects.all()
    return Response(UserSerializer(users, many=True).data)


# ------- Admin management (super_admin only) -------

def _require_super_admin(user):
    return user.role == 'super_admin'


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admins_list(request):
    if not _require_super_admin(request.user):
        return Response({'error': 'Only the super admin can manage admins'},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        admins = User.objects.filter(role='admin').order_by('-created_at')
        return Response(UserSerializer(admins, many=True).data)

    email = request.data.get('email', '').strip()
    password = request.data.get('password')
    first_name = request.data.get('first_name', '').strip()
    last_name = request.data.get('last_name', '').strip()
    phone = request.data.get('phone', '')

    if not email or not password or not first_name or not last_name:
        return Response({'error': 'Email, password, first name and last name are required'},
                        status=status.HTTP_400_BAD_REQUEST)
    if len(password) < 6:
        return Response({'error': 'Password must be at least 6 characters'},
                        status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        return Response({'error': 'A user with this email already exists'},
                        status=status.HTTP_400_BAD_REQUEST)

    admin = User.objects.create_user(
        email=email, password=password,
        first_name=first_name, last_name=last_name,
        phone=phone, role='admin', is_staff=True,
    )
    return Response(UserSerializer(admin).data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def admin_detail(request, id):
    if not _require_super_admin(request.user):
        return Response({'error': 'Only the super admin can manage admins'},
                        status=status.HTTP_403_FORBIDDEN)
    try:
        admin = User.objects.get(id=id, role='admin')
    except User.DoesNotExist:
        return Response({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(UserSerializer(admin).data)

    if request.method in ['PUT', 'PATCH']:
        for field in ['first_name', 'last_name', 'phone', 'is_active']:
            if field in request.data:
                setattr(admin, field, request.data.get(field))
        new_password = request.data.get('password')
        if new_password:
            if len(new_password) < 6:
                return Response({'error': 'Password must be at least 6 characters'},
                                status=status.HTTP_400_BAD_REQUEST)
            admin.set_password(new_password)
        admin.save()
        return Response(UserSerializer(admin).data)

    admin.delete()
    return Response({'message': 'Admin deleted'}, status=status.HTTP_204_NO_CONTENT)