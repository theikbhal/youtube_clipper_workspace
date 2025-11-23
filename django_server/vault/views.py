from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Account

@login_required
def dashboard(request):
    accounts = Account.objects.all().order_by('-created_at')
    return render(request, 'vault/dashboard.html', {'accounts': accounts})
