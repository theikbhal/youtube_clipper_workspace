import json
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import GoLink


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
