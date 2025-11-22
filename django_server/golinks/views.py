import json
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect

from .models import GoLink


def go_home(request):
    return redirect("/go/ui/")

@csrf_exempt
def golinks(request):
    # LIST
    if request.method == "GET":
        data = list(GoLink.objects.values())
        return JsonResponse({"success": True, "data": data})

    # CREATE
    if request.method == "POST":
        body = json.loads(request.body)
        link = GoLink.objects.create(
            key=body["key"],
            url=body["url"],
            description=body.get("description", "")
        )
        return JsonResponse({"success": True, "id": link.id})

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
def golink_detail(request, key):
    link = get_object_or_404(GoLink, key=key)

    # GET ONE
    if request.method == "GET":
        return JsonResponse({
            "key": link.key,
            "url": link.url,
            "description": link.description
        })

    # UPDATE
    if request.method == "PUT":
        body = json.loads(request.body)
        link.url = body.get("url", link.url)
        link.description = body.get("description", link.description)
        link.save()
        return JsonResponse({"success": True})

    # DELETE
    if request.method == "DELETE":
        link.delete()
        return JsonResponse({"success": True})

    return HttpResponseNotAllowed(["GET", "PUT", "DELETE"])


def go_redirect(request, key):
    link = get_object_or_404(GoLink, key=key)
    return HttpResponseRedirect(link.url)


def golinks_ui(request):
    """
    Simple web page:
    - GET: show form + list
    - POST: create or update a GoLink
    """
    if request.method == "POST":
        key = request.POST.get("key", "").strip()
        url = request.POST.get("url", "").strip()
        description = request.POST.get("description", "").strip()

        if key and url:
            # if key exists, update; otherwise create
            GoLink.objects.update_or_create(
                key=key,
                defaults={"url": url, "description": description},
            )

        # After saving, redirect to avoid form re-submit on refresh
        return redirect("golinks_ui")

    # GET: show all links
    links = GoLink.objects.all().order_by("key")
    return render(request, "golinks/manage.html", {"links": links})


def delete_golink(request, key):
    link = get_object_or_404(GoLink, key=key)
    link.delete()
    return redirect("golinks_ui")
