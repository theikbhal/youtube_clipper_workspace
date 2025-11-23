from django.db import models

class Account(models.Model):
    CATEGORY_CHOICES = [
        ('email', 'Email Account'),
        ('replit', 'Replit Account'),
        ('ssh', 'SSH Key'),
        ('other', 'Other'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('free', 'Free'),
        ('paid', 'Paid'),
    ]

    name = models.CharField(max_length=255, help_text="Name of the service or account")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    username = models.CharField(max_length=255, blank=True, help_text="Username or Email")
    password = models.CharField(max_length=255, blank=True, help_text="Password or Key (stored as plain text)")
    
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='free')
    paid_by = models.CharField(max_length=255, blank=True, help_text="Who pays for this")
    card_used = models.CharField(max_length=255, blank=True, help_text="Which card was used")
    payment_start_date = models.DateField(null=True, blank=True)
    reminder_days_before = models.IntegerField(null=True, blank=True, help_text="Days to remind before renewal/expiry")
    
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
