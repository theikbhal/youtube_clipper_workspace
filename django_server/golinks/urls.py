from django.urls import path
from .views import golinks, golink_detail, go_redirect, golinks_ui, delete_golink, go_home

urlpatterns = [

    path("", go_home, name="golinks_home"),   # ✅ redirect /go/ → /go/ui/
    path("ui/", golinks_ui, name="golinks_ui"),

    # API
    path("api/", golinks),
    path("api/<str:key>/", golink_detail),
    path("delete/<str:key>/", delete_golink, name="delete_golink"),


    # Redirect
    path("<str:key>/", go_redirect),
]
