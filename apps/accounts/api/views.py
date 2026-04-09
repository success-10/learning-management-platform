from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import UserSerializer, RegistrationSerializer
from apps.accounts.models import User
from .throttles import RegistrationRateThrottle
from apps.accounts.services import AccountService
from apps.core.mixins import AuditMixin


class UserViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can see themselves, Admins can see all
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMIN:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], throttle_classes=[RegistrationRateThrottle])
    def register(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = AccountService.register_user(
            **serializer.validated_data,
            **self.get_audit_context()
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
