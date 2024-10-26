from django.shortcuts import render

def index(request):
    return render(request, 'index.html')  # Replace 'index.html' with the correct template name if different
