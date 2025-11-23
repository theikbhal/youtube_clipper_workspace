from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("home.urls")),
    path('admin/', admin.site.urls),
    path('clips/', include('clips.urls')),
    path("go/", include("golinks.urls")),
    path("apkgen/", include("apkgen.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)