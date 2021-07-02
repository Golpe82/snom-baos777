from django.shortcuts import redirect, render
from django.conf import settings

from lists.models import Item


APP = 'TO-DO'

def home_page(request):
    context = {
        'project': settings.PROJECT_NAME,
        'app': APP,
        'page': 'Start a new To-Do list',
    }

    return render(request, 'home.html', context)

def view_list(request):
    items = Item.objects.all()

    context = {
        "items": items,
        'project': settings.PROJECT_NAME,
        'app': APP,
        'page': 'To-Do list',
    }

    return render(request, 'list.html', context)

def new_list(request):
    Item.objects.create(text=request.POST["item_text"])
    return redirect("/lists/the-only-list-in-the-world/")



