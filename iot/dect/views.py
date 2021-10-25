from django.shortcuts import render

def home(request):
    context = {}

    return render(request, 'dect/dect_home.html', context)
