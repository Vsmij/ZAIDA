from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.middleware.csrf import get_token
from datetime import datetime
from .serializers import MeasurementSerializer, SeriesSerializer, SeriesColorSerializer
from .models import Series, Measurement
#from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
#for render
from django.shortcuts import render

User = get_user_model()

#render
def index_frontend(request):
    return render(request, 'index.html')

# === REJESTRACJA ===
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"detail": "Email i hasło wymagane."}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"detail": "Email już zajęty."}, status=400)

    try:
        validate_password(password, user=None)
    except ValidationError as e:
        return Response(
            {"detail": list(e.messages)},
            status=400
        )

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password
    )
    return Response({"detail": "Konto utworzone."}, status=201)


# === LOGOWANIE ===
@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
#@csrf_exempt
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(email=email, password=password)
    if user:
        login(request, user)
        return Response({"detail": "Zalogowano."})
    return Response({"detail": "Błędne dane."}, status=401)


# === DANE UŻYTKOWNIKA ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication])
def me_view(request):
    return Response({
        "email": request.user.email,
        "is_admin": request.user.is_staff
    })


# === ZMIANA HASŁA ===
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication])
def change_password_view(request):
    form = SetPasswordForm(user=request.user, data=request.data)
    if form.is_valid():
        form.save()
        return Response({"detail": "Hasło zmienione."})
    return Response(form.errors, status=400)

# === SERIE ===
#był ReadOnlyModelViewSet
class SeriesViewSet(viewsets.ModelViewSet):
    queryset = Series.objects.all().order_by('-date')
    serializer_class = SeriesSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'date'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrowanie po dacie
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Filtrowanie pomiarów po godzinie
        measurements = instance.measurements.all().order_by('timestamp')
        start_hour = request.query_params.get('start_hour')
        end_hour = request.query_params.get('end_hour')
        if start_hour:
            measurements = measurements.filter(timestamp__hour__gte=int(start_hour))
        if end_hour:
            measurements = measurements.filter(timestamp__hour__lte=int(end_hour))

        data = serializer.data
        data['measurements'] = MeasurementSerializer(measurements, many=True).data
        return Response(data)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def color(self, request, date=None):
        series = self.get_object()
        #serializer = serializers.ModelSerializer(series, data=request.data, partial=True, fields=('color',))
        serializer = SeriesColorSerializer(series, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'timestamp'

    def perform_create(self, serializer):
        #permission_classes = [permissions.IsAdminUser]
        serializer.save()

# Create your views here.
