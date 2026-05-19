from django.db import models
from django.contrib.auth.models import User
import markdown2

class Books(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    isbn = models.CharField(max_length=20)
    page_number = models.IntegerField()
    description = models.TextField()
    language = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.ForeignKey("Authors", on_delete=models.CASCADE, related_name='books')
    publication = models.ForeignKey("Publications", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ['-date']

    def __str__(self):
        return self.title

class Authors(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        return self.name

class Publications(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()

    class Meta:
        verbose_name = "Publication"
        verbose_name_plural = "Publications"

    def __str__(self):
        return self.name

class Book_genres(models.Model):
    book = models.ForeignKey("Books", on_delete=models.CASCADE)
    genre = models.ForeignKey("Genres", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Book Genre"
        verbose_name_plural = "Book Genres"

    def __str__(self):
        return f"{self.book.title} - {self.genre.name}"

class Genres(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"

    def __str__(self):
        return self.name
    

class Comments(models.Model):
    review = models.ForeignKey("Reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user.username} on {self.review.book.title}"

class Reviews(models.Model):
    book = models.ForeignKey("Books", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    spoilers = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self):
        return f"Review for {self.book.title} by {self.user.username}"

class Book_list(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    books = models.ManyToManyField("Books")
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Book List"
        verbose_name_plural = "Book Lists"

    def __str__(self):
        return self.title

class Books_in_list(models.Model):
    book_list = models.ForeignKey("Book_list", on_delete=models.CASCADE)
    book = models.ForeignKey("Books", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Book in List"
        verbose_name_plural = "Books in List"

    def __str__(self):
        return f"{self.book.title} in {self.book_list.title}"

class Reading_status(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey("Books", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('not started', 'Not Started'), ('reading', 'Reading'), ('finished', 'Finished')])

    class Meta:
        verbose_name = "Reading Status"
        verbose_name_plural = "Reading Statuses"

    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.status}"

class Favourites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey("Books", on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Favourite"
        verbose_name_plural = "Favourites"

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
    
class Post(models.Model):
    title = models.CharField(max_lenght=200)
    content = models.TextField()

    def __str__(self):
        return self.title
    
    