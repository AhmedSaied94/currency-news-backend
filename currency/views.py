from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt


# Create your views here.

@xframe_options_exempt
def iframe(request):
    return render(request, 'currency/iframe.js', content_type='text/javascript')
