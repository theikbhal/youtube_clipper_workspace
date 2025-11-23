from django.shortcuts import render

def home(request):
    apps = [
        {
            "name": "Go Links",
            "url": "/go/"
        },
        {
            "name": "YouTube Clipper",
            "url": "/clips/"
        },
        {
            "name": "Vault (Password Manager)",
            "url": "/admin/vault/account/"
        },
        {
            "name": "APK Generator",
            "url": "/apkgen/"
        },
        # Add more apps here later
    ]
    return render(request, "home.html", {"apps": apps})
