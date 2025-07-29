import geoip2.database
from django.utils.timezone import now
from .models import PrayerActivity

GEOIP_DB_PATH = 'geo/GeoLite2-City.mmdb'  # You’ll download this below

class TrackUserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.reader = geoip2.database.Reader(GEOIP_DB_PATH)

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            ip = get_client_ip(request)
            region = "Unknown"
            try:
                geo = self.reader.city(ip)
                region = geo.subdivisions.most_specific.name or geo.country.name
            except:
                pass
            PrayerActivity.objects.update_or_create(
                user=request.user,
                defaults={'region': region, 'last_active': now()}
            )
        return response

def get_client_ip(request):
    return request.META.get('REMOTE_ADDR', '')
