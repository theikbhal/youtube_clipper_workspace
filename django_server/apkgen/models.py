from django.db import models

class ApkBuild(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    app_name = models.CharField(max_length=50)
    package_name = models.CharField(max_length=100)
    apk_file = models.FileField(upload_to="apkgen/")

    def __str__(self):
        return f"{self.app_name} ({self.package_name})"
