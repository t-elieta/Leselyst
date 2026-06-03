from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from .models import Books, Authors, Reviews, Comments, Book_list, Reading_status, Favourites, ReadingChallenge, UserProfile
from django.db.models import Q, Count
from django.utils import timezone


def home(request):
    books = Books.objects.all().order_by("-date")[:10]
    trending = Books.objects.annotate(fav_count=Count('favourites')).order_by('-fav_count')[:8]
    reading_now = Books.objects.annotate(reading_count=Count('reading_status', filter=Q(reading_status__status='reading'))).filter(reading_count__gt=0).order_by('-reading_count')[:8]
    public_lists = Book_list.objects.filter(is_public=True).order_by('-created_at')[:6]
    return render(request, "home.html", {
        "books": books,
        "trending": trending,
        "reading_now": reading_now,
        "public_lists": public_lists,
    })


def book_list(request):
    valid_sorts = ['-date', 'date', 'title', '-title', 'author__name']
    sort = request.GET.get("sort", "-date")
    if sort not in valid_sorts:
        sort = "-date"
    books = Books.objects.all().order_by(sort)
    return render(request, "book_list.html", {"books": books, "sort": sort})


def book_detail(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    reviews = Reviews.objects.filter(book=book).order_by("-datetime")
    reading_status = None
    is_favourite = False
    lists = []
    if request.user.is_authenticated:
        reading_status = Reading_status.objects.filter(user=request.user, book=book).first()
        is_favourite = Favourites.objects.filter(user=request.user, book=book).exists()
        lists = Book_list.objects.filter(user=request.user)
    return render(request, "book_detail.html", {
        "book": book,
        "reviews": reviews,
        "reading_status": reading_status,
        "is_favourite": is_favourite,
        "lists": lists,
    })


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


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_profile, _ = UserProfile.objects.get_or_create(user=profile_user)
    year = timezone.now().year
    month = timezone.now().month

    total_read = Reading_status.objects.filter(user=profile_user, status='finished').count()
    reading_now = Reading_status.objects.filter(user=profile_user, status='reading').count()
    total_reviews = Reviews.objects.filter(user=profile_user).count()
    total_favourites = Favourites.objects.filter(user=profile_user).count()
    read_this_month = Reading_status.objects.filter(
        user=profile_user, status='finished',
        book__date__year=year, book__date__month=month
    ).count()

    challenge = ReadingChallenge.objects.filter(user=profile_user, year=year).first()
    progress_pct = 0
    if challenge and challenge.goal > 0:
        progress_pct = min(int((total_read / challenge.goal) * 100), 100)

    currently_reading = Reading_status.objects.filter(user=profile_user, status='reading').select_related('book')[:8]
    recently_finished = Reading_status.objects.filter(user=profile_user, status='finished').select_related('book')[:8]
    public_lists = Book_list.objects.filter(user=profile_user, is_public=True).order_by('-created_at')

    return render(request, "profile.html", {
        "profile_user": profile_user,
        "user_profile": user_profile,
        "year": year,
        "total_read": total_read,
        "reading_now": reading_now,
        "total_reviews": total_reviews,
        "total_favourites": total_favourites,
        "read_this_month": read_this_month,
        "challenge": challenge,
        "progress_pct": progress_pct,
        "currently_reading": currently_reading,
        "recently_finished": recently_finished,
        "public_lists": public_lists,
    })


@login_required
def set_challenge(request):
    year = timezone.now().year
    challenge = ReadingChallenge.objects.filter(user=request.user, year=year).first()
    total_read = Reading_status.objects.filter(user=request.user, status='finished').count()
    progress_pct = 0
    if challenge and challenge.goal > 0:
        progress_pct = min(int((total_read / challenge.goal) * 100), 100)
    if request.method == "POST":
        goal = request.POST.get("goal")
        end_date = request.POST.get("end_date") or None
        if goal:
            ReadingChallenge.objects.update_or_create(
                user=request.user,
                year=year,
                defaults={"goal": int(goal), "end_date": end_date}
            )
        return redirect("Leselystapp:profile", username=request.user.username)
    return render(request, "set_challenge.html", {
        "challenge": challenge,
        "year": year,
        "total_read": total_read,
        "progress_pct": progress_pct,
    })


@login_required
def account_settings(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    success = None
    error = None

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "profile":
            request.user.first_name = request.POST.get("first_name", "")
            request.user.last_name = request.POST.get("last_name", "")
            request.user.email = request.POST.get("email", "")
            request.user.save()
            user_profile.avatar = request.POST.get("avatar", "") or None
            user_profile.bio = request.POST.get("bio", "")
            user_profile.save()
            success = "Profile updated successfully."

        elif form_type == "password":
            current = request.POST.get("current_password")
            new_pw = request.POST.get("new_password")
            confirm = request.POST.get("confirm_password")
            if not request.user.check_password(current):
                error = "Current password is incorrect."
            elif new_pw != confirm:
                error = "New passwords do not match."
            elif len(new_pw) < 8:
                error = "Password must be at least 8 characters."
            else:
                request.user.set_password(new_pw)
                request.user.save()
                login(request, request.user)
                success = "Password changed successfully."

    return render(request, "account_settings.html", {
        "user_profile": user_profile,
        "success": success,
        "error": error,
    })


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
            defaults={"rating": rating, "description": description, "spoilers": spoilers}
        )
        return redirect("Leselystapp:book_detail", book_id=book.id)
    return redirect("Leselystapp:book_detail", book_id=book.id)


@login_required
def add_comment(request, review_id):
    review = get_object_or_404(Reviews, id=review_id)
    if request.method == "POST":
        comment_text = request.POST.get("comment")
        if comment_text:
            Comments.objects.create(review=review, user=request.user, comment=comment_text)
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
                user=request.user, book=book, defaults={"status": status}
            )
    return redirect("Leselystapp:book_detail", book_id=book.id)


@login_required
def my_lists(request):
    lists = Book_list.objects.filter(user=request.user)
    reading = Reading_status.objects.filter(user=request.user, status='reading')
    finished = Reading_status.objects.filter(user=request.user, status='finished')
    favourites = Favourites.objects.filter(user=request.user)
    return render(request, "my_lists.html", {
        "lists": lists,
        "reading": reading,
        "finished": finished,
        "favourites": favourites,
    })


def list_detail(request, list_id):
    book_list = get_object_or_404(Book_list, id=list_id, user=request.user)
    if not book_list.is_public and book_list.user != request.user:
        return redirect("Leselystapp:home")
    return render(request, "list_detail.html", {"book_list": book_list})


@login_required
def create_list(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        is_public = request.POST.get("is_public") == "on"
        if title:
            Book_list.objects.create(
                user=request.user, title=title,
                description=description, is_public=is_public
            )
        return redirect("Leselystapp:my_lists")
    return render(request, "create_list.html")


@login_required
def edit_list(request, list_id):
    book_list = get_object_or_404(Book_list, id=list_id, user=request.user)
    all_books = Books.objects.all().order_by("title")
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        is_public = request.POST.get("is_public") == "on"
        selected_books = request.POST.getlist("books")
        if title:
            book_list.title = title
            book_list.description = description
            book_list.is_public = is_public
            book_list.save()
            book_list.books.set(selected_books)
        return redirect("Leselystapp:my_lists")
    return render(request, "edit_list.html", {"book_list": book_list, "all_books": all_books})


@login_required
def add_to_list(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    if request.method == "POST":
        list_id = request.POST.get("list_id")
        if list_id:
            book_list = get_object_or_404(Book_list, id=list_id, user=request.user)
            book_list.books.add(book)
        return redirect("Leselystapp:book_detail", book_id=book.id)
    lists = Book_list.objects.filter(user=request.user)
    return render(request, "book_detail.html", {"book": book, "lists": lists})


def search(request):
    query = request.GET.get("q", "")
    if query:
        results = Books.objects.filter(
            Q(title__icontains=query) | Q(author__name__icontains=query)
        ).order_by("-date")
    else:
        results = Books.objects.none()
    return render(request, "search_results.html", {"results": results, "query": query})