from ipaddress import ip_address

from django.conf import settings
from django.shortcuts import render


class ZimbabweCountryAccessMiddleware:
    protected_paths = (
        '/login/',
        '/accounts/signup/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._should_check_request(request) and not self._is_request_allowed(request):
            return render(
                request,
                'accounts/location_blocked.html',
                status=403,
            )
        return self.get_response(request)

    def _should_check_request(self, request):
        if not getattr(settings, 'ZIMBABWE_IP_RESTRICTION_ENABLED', True):
            return False

        path = request.path.rstrip('/') + '/'
        return path in self.protected_paths

    def _is_request_allowed(self, request):
        country_code = self._get_country_code(request)
        if country_code:
            return country_code == 'ZW'

        if getattr(settings, 'DEBUG', False) and self._is_local_request(request):
            return True

        return not getattr(settings, 'ZIMBABWE_IP_BLOCK_ON_MISSING_COUNTRY', True)

    def _get_country_code(self, request):
        for header_name in getattr(settings, 'ZIMBABWE_GEOIP_HEADER_CANDIDATES', []):
            header_value = request.META.get(header_name, '').strip().upper()
            if header_value:
                return header_value
        return ''

    def _is_local_request(self, request):
        remote_addr = request.META.get('REMOTE_ADDR', '')
        if not remote_addr:
            return False

        try:
            client_ip = ip_address(remote_addr)
        except ValueError:
            return False

        return client_ip.is_loopback or client_ip.is_private
