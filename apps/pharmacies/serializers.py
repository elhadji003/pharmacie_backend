from rest_framework import serializers

from .models import DutySchedule, Pharmacy


class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = (
            'id',
            'name',
            'address',
            'city',
            'postal_code',
            'phone',
            'latitude',
            'longitude',
            'is_active',
        )


class DutyScheduleSerializer(serializers.ModelSerializer):
    pharmacy = PharmacySerializer(read_only=True)
    pharmacy_id = serializers.PrimaryKeyRelatedField(
        queryset=Pharmacy.objects.all(),
        source='pharmacy',
        write_only=True,
    )

    class Meta:
        model = DutySchedule
        fields = (
            'id',
            'pharmacy',
            'pharmacy_id',
            'starts_at',
            'ends_at',
            'notes',
        )

    def validate(self, attrs):
        starts_at = attrs.get('starts_at', getattr(self.instance, 'starts_at', None))
        ends_at = attrs.get('ends_at', getattr(self.instance, 'ends_at', None))
        if starts_at and ends_at and ends_at <= starts_at:
            raise serializers.ValidationError(
                {'ends_at': "La fin de la garde doit être après son début."}
            )
        return attrs
