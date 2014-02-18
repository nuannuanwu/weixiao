from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from api.views import api_not_found


def dispath_404(request, template_name="404.html"):
    ctx = {}
    app = request.path.split("/")[1]
    if app == "api":
        return api_not_found(request)
    return render(request, template_name, ctx)
