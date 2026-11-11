from rest_framework.routers import DefaultRouter

from .views import DutyScheduleViewSet, PharmacyViewSet

router = DefaultRouter()
router.register('pharmacies', PharmacyViewSet, basename='pharmacy')
router.register('guards', DutyScheduleViewSet, basename='guard')

urlpatterns = router.urls
