from django.contrib import admin
from .models import Account

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'username', 'payment_status', 'paid_by', 'payment_start_date')
    list_filter = ('category', 'payment_status', 'paid_by')
    search_fields = ('name', 'username', 'notes', 'paid_by')
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'username', 'password', 'notes')
        }),
        ('Payment Details', {
            'fields': ('payment_status', 'paid_by', 'card_used', 'payment_start_date', 'reminder_days_before'),
        }),
    )
