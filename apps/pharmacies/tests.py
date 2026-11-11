from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import DutySchedule, Pharmacy


class PharmacyApiTests(APITestCase):
    def setUp(self):
        self.pharmacy = Pharmacy.objects.create(
            name='Pharmacie Centrale',
            address='1 rue de la Paix',
            city='Paris',
            postal_code='75001',
            phone='0102030405',
            latitude=48.8566,
            longitude=2.3522,
        )

    def test_public_pharmacy_search_filters_city_case_insensitively(self):
        response = self.client.get(reverse('pharmacy-list'), {'city': 'paris'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Pharmacie Centrale')

    def test_public_duty_search_filters_city_and_date(self):
        now = timezone.now()
        duty = DutySchedule.objects.create(
            pharmacy=self.pharmacy,
            starts_at=now,
            ends_at=now + timedelta(hours=8),
        )

        response = self.client.get(
            reverse('guard-list'),
            {'city': 'Paris', 'date': now.date().isoformat()},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item['id'] for item in response.data], [duty.id])
        self.assertEqual(response.data[0]['pharmacy']['name'], self.pharmacy.name)

    def test_invalid_date_returns_bad_request(self):
        response = self.client.get(reverse('guard-list'), {'date': 'not-a-date'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date', response.data)

    def test_inactive_pharmacies_are_hidden_from_public_search(self):
        self.pharmacy.is_active = False
        self.pharmacy.save(update_fields=('is_active',))

        response = self.client.get(reverse('pharmacy-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_staff_can_manage_inactive_pharmacies(self):
        self.pharmacy.is_active = False
        self.pharmacy.save(update_fields=('is_active',))
        staff_user = get_user_model().objects.create_user(
            username='manager',
            password='test-password',
            is_staff=True,
        )
        self.client.force_authenticate(user=staff_user)

        response = self.client.get(
            reverse('pharmacy-detail', kwargs={'pk': self.pharmacy.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.pharmacy.pk)

    def test_anonymous_user_cannot_create_pharmacy(self):
        response = self.client.post(
            reverse('pharmacy-list'),
            {
                'name': 'Nouvelle pharmacie',
                'address': '2 rue Exemple',
                'city': 'Paris',
                'postal_code': '75002',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Pharmacy.objects.count(), 1)

    def test_staff_user_can_create_pharmacy(self):
        staff_user = get_user_model().objects.create_user(
            username='manager',
            password='test-password',
            is_staff=True,
        )
        self.client.force_authenticate(user=staff_user)

        response = self.client.post(
            reverse('pharmacy-list'),
            {
                'name': 'Nouvelle pharmacie',
                'address': '2 rue Exemple',
                'city': 'Paris',
                'postal_code': '75002',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pharmacy.objects.count(), 2)
