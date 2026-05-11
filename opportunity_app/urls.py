import os

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path, re_path
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('accounts/', include('accounts.urls')),
    path('logout/', LogoutView.as_view(next_page='welcome'), name='logout'),
]

# When DEBUG is False, runserver does not serve STATICFILES_DIRS. Teammates with
# DJANGO_DEBUG=false then see completely unstyled pages. Serve /static/ from the
# repo `static/` folder unless disabled (e.g. production behind nginx + collectstatic).
_serve_static = os.getenv('DJANGO_SERVE_STATIC', 'true').lower() in ('1', 'true', 'yes')
if _serve_static and getattr(settings, 'STATICFILES_DIRS', None):
    urlpatterns += [
        re_path(
            r'^static/(?P<path>.*)$',
            serve,
            {'document_root': str(settings.STATICFILES_DIRS[0])},
        ),
    ]
