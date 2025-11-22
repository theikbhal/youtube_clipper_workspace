from django.db import models

class GoLink(models.Model):
    key = models.CharField(max_length=100, unique=True)
    url = models.URLField()
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.key} -> {self.url}"
