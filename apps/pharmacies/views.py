from datetime import datetime, time, timedelta

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import DutySchedule, Pharmacy
from .permissions import PublicReadAdminWrite
from .serializers import DutyScheduleSerializer, PharmacySerializer


def parse_search_date(value):
    try:
        search_date = datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError as exc:
        raise ValidationError(
            {'date': 'Utilisez le format YYYY-MM-DD pour la date.'}
        ) from exc
    if search_date.isoformat() != value:
        raise ValidationError(
            {'date': 'Utilisez le format YYYY-MM-DD pour la date.'}
        )

    current_timezone = timezone.get_current_timezone()
    start_of_day = timezone.make_aware(
        datetime.combine(search_date, time.min),
        current_timezone,
    )
    return start_of_day, start_of_day + timedelta(days=1)


class PharmacyViewSet(viewsets.ModelViewSet):
    serializer_class = PharmacySerializer
    permission_classes = (PublicReadAdminWrite,)

    def get_queryset(self):
        queryset = Pharmacy.objects.all()
        if not getattr(self.request.user, 'is_staff', False):
            queryset = queryset.filter(is_active=True)
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__iexact=city.strip())
        return queryset


class DutyScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = DutyScheduleSerializer
    permission_classes = (PublicReadAdminWrite,)

    def get_queryset(self):
        queryset = DutySchedule.objects.select_related('pharmacy')
        if not getattr(self.request.user, 'is_staff', False):
            queryset = queryset.filter(pharmacy__is_active=True)
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(pharmacy__city__iexact=city.strip())

        search_date = self.request.query_params.get('date')
        if search_date:
            start_of_day, start_of_next_day = parse_search_date(search_date)
            queryset = queryset.filter(
                starts_at__lt=start_of_next_day,
                ends_at__gt=start_of_day,
            )
        return queryset
