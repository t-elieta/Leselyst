from django.shortcuts import render
from .models import Books

def home(request):
    books = Books.objects.all()
    return render(request, 'home.html', {'books': books})
