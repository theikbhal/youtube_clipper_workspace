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
        # Add more apps here later
    ]
    return render(request, "home.html", {"apps": apps})
