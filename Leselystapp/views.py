from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .models import Books, Authors, Reviews, Comments, Book_list, Reading_status, Favourites
from django.db.models import Q

def home(request):
    books = Books.objects.all().order_by("-date")[:10]
    return render(request, "home.html", {"books": books})


def book_list(request):
    books = Books.objects.all().order_by("-date")
    return render(request, "book_list.html", {"books": books})


def book_detail(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    reviews = Reviews.objects.filter(book=book).order_by("-datetime")
    return render(request, "book_detail.html", {"book": book, "reviews": reviews})


def author_list(request):
    authors = Authors.objects.all().order_by("name")
    return render(request, "author_list.html", {"authors": authors})


def author_detail(request, author_id):
    author = get_object_or_404(Authors, id=author_id)
    books = Books.objects.filter(author=author).order_by("-date")
    return render(request, "author_detail.html", {"author": author, "books": books})


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("Leselystapp:home")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("index")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get("next", "index"))
        return render(request, "login.html", {
            "username": username, "error": "Wrong password"
        })
    return render(request, "login.html")

@login_required
def add_review(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    if request.method == "POST":
        rating = request.POST.get("rating")
        description = request.POST.get("description")
        spoilers = request.POST.get("spoilers") == "on"
        Reviews.objects.update_or_create(
            user=request.user,
            book=book,
            defaults={
                "rating": rating,
                "description": description,
                "spoilers": spoilers,
            }
        )
        return redirect("Leselystapp:book_detail", book_id=book.id)
    return redirect("Leselystapp:book_detail", book_id=book.id)
    

@login_required
def add_comment(request, review_id):
    review = get_object_or_404(Reviews, id=review_id)
    if request.method == "POST":
        comment_text = request.POST.get("comment")
        if comment_text:
            Comments.objects.create(
                review=review,
                user=request.user,
                comment=comment_text
            )
    return redirect("Leselystapp:book_detail", book_id=review.book.id)
    

@login_required
def toggle_favourite(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    favourite, created = Favourites.objects.get_or_create(user=request.user, book=book)
    if not created:
        favourite.delete()
    return redirect("Leselystapp:book_detail", book_id=book.id)
    

@login_required
def set_reading_status(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    if request.method == "POST":
        status = request.POST.get("status")
        if status:
            Reading_status.objects.update_or_create(
                user=request.user,
                book=book,
                defaults={"status": status}
            )
    return redirect("Leselystapp:book_detail", book_id=book.id)


@login_required
def my_lists(request):
   lists = Book_list.objects.filter(user=request.user)
   return render(request, "my_lists.html", {"lists": lists})


@login_required
def list_detail(request, list_id):
    book_list = get_object_or_404(Book_list, id=list_id, user=request.user)
    if not book_list.is_public and book_list.user != request.user:
        return redirect("Leselystapp:home")
    return render(request, "list_detail.html", {"book_list": book_list})


#def search(request):
