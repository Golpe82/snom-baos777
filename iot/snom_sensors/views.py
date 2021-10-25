from django.shortcuts import render

def home(request):
    context = {}

    return render(request, 'snom_sensors/snom_sensors_home.html', context)
