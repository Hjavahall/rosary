from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rosary.models import PrayerActivity
from django.utils.timezone import now, timedelta
import random

REGIONS = [
    ('California', 36.7783, -119.4179),
    ('England', 52.3555, -1.1743),
    ('Ontario', 51.2538, -85.3232),
    ('Nigeria', 9.0820, 8.6753),
    ('India', 20.5937, 78.9629),
    ('Brazil', -14.2350, -51.9253),
    ('Philippines', 13.4100, 122.5600),
    ('Poland', 51.9194, 19.1451),
    ('Vietnam', 14.0583, 108.2772),
    ('South Africa', -30.5595, 22.9375),
]

class Command(BaseCommand):
    help = "Seed prayer activity with fake user locations"

    def handle(self, *args, **kwargs):
        for i, (region, lat, lng) in enumerate(REGIONS):
            username = f"testuser{i+1}"
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password("testpass123")
                user.save()

            PrayerActivity.objects.update_or_create(
                user=user,
                defaults={
                    'region': region,
                    'lat': lat,
                    'lng': lng,
                    'last_active': now() - timedelta(minutes=random.randint(1, 14)),
                }
            )
        self.stdout.write(self.style.SUCCESS("Seeded 10 fake prayer activities"))
