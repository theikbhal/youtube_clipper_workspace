from django.urls import path
from . import views

urlpatterns = [
    path("ui/", views.apk_form, name="apkgen_ui"),
    path("build/", views.build_apk, name="apkgen_build"),
]
