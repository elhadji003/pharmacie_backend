from django.contrib import admin

from .models import DutySchedule, Pharmacy


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'postal_code', 'phone', 'is_active')
    list_filter = ('city', 'is_active')
    search_fields = ('name', 'city', 'postal_code', 'address')


@admin.register(DutySchedule)
class DutyScheduleAdmin(admin.ModelAdmin):
    list_display = ('pharmacy', 'starts_at', 'ends_at')
    list_filter = ('starts_at', 'pharmacy__city')
    search_fields = ('pharmacy__name', 'pharmacy__city')
