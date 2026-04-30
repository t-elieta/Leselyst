from django.shortcuts import render
from .models import Books

def home(request):
    books = Books.objects.all()
    return render(request, 'home.html', {'books': books})

def book_list(request):
    books = Books.objects.all()
    return render(request, 'book_list.html', {'books': books})

def book_detail(request, book_id):
    book = Books.objects.get(id=book_id)
    return render(request, 'book_detail.html', {'book': book})

def author_list(request):
    authors = Books.objects.values_list('author', flat=True).distinct()
    return render(request, 'author_list.html', {'authors': authors})

def author_detail(request, author_name):
    books = Books.objects.filter(author=author_name)
    return render(request, 'author_detail.html', {'books': books})
