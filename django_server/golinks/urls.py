from django.urls import path
from .views import golinks, golink_detail, go_redirect

urlpatterns = [
    # API
    path("api/", golinks),
    path("api/<str:key>/", golink_detail),

    # Redirect
    path("<str:key>/", go_redirect),
]
