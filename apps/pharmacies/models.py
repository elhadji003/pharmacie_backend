from django.db import models
from django.db.models import F, Q


class Pharmacy(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, db_index=True)
    postal_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=30, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('city', 'name')

    def __str__(self):
        return f'{self.name} - {self.city}'


class DutySchedule(models.Model):
    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name='duties',
    )
    starts_at = models.DateTimeField(db_index=True)
    ends_at = models.DateTimeField(db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('starts_at',)
        constraints = [
            models.CheckConstraint(
                condition=Q(ends_at__gt=F('starts_at')),
                name='duty_ends_after_starts',
            ),
        ]

    def __str__(self):
        return f'{self.pharmacy} ({self.starts_at} - {self.ends_at})'
