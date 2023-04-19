from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .settings import DEBUG, MEDIA_URL, MEDIA_ROOT

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace="api")),
]

if DEBUG:
    urlpatterns += static(
        MEDIA_URL, document_root=MEDIA_ROOT
    )
