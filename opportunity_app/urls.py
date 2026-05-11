import os

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path, re_path
from django.views.static import serve

# When DEBUG is False, runserver does not serve STATICFILES_DIRS. Also, `path('', include(...))`
# matches *every* URL including `/static/...`, so static routes MUST come before that catch-all
# or they are never reached (pages.urls has no static/* patterns → 404).
_serve_static = os.getenv('DJANGO_SERVE_STATIC', 'true').lower() in ('1', 'true', 'yes')
_static_urlpatterns = []
if _serve_static and getattr(settings, 'STATICFILES_DIRS', None):
    _static_urlpatterns = [
        re_path(
            r'^static/(?P<path>.*)$',
            serve,
            {'document_root': str(settings.STATICFILES_DIRS[0])},
        ),
    ]

urlpatterns = [
    path('admin/', admin.site.urls),
    *_static_urlpatterns,
    path('', include('pages.urls')),
    path('accounts/', include('accounts.urls')),
    path('logout/', LogoutView.as_view(next_page='welcome'), name='logout'),
]
