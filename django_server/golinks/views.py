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
    # ----------------------------
    # HANDLE CREATE / UPDATE
    # ----------------------------
    if request.method == "POST":
        key = request.POST.get("key", "").strip()
        url = request.POST.get("url", "").strip()
        description = request.POST.get("description", "").strip()

        if key and url:
            GoLink.objects.update_or_create(
                key=key,
                defaults={"url": url, "description": description},
            )

        return redirect("golinks_ui")

    # ----------------------------
    # HANDLE FILTER BY KEY
    # ----------------------------
    search_key = request.GET.get("search", "").strip()

    if search_key:
        links = GoLink.objects.filter(key__icontains=search_key).order_by("key")
    else:
        links = GoLink.objects.all().order_by("key")

    # ----------------------------
    # HANDLE EDIT PREFILL
    # ----------------------------
    edit_key = request.GET.get("edit", "").strip()
    edit_link = None

    if edit_key:
        try:
            edit_link = GoLink.objects.get(key=edit_key)
        except GoLink.DoesNotExist:
            edit_link = None

    return render(request, "golinks/manage.html", {
        "links": links,
        "edit_link": edit_link,
        "search_key": search_key
    })


def delete_golink(request, key):
    link = get_object_or_404(GoLink, key=key)
    link.delete()
    return redirect("golinks_ui")
