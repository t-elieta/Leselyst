from django.contrib import admin
from .models import Books, Authors, Publications, Book_genres, Genres

admin.site.register(Books)
admin.site.register(Authors)
admin.site.register(Publications)
admin.site.register(Book_genres)
admin.site.register(Genres)
admin.site.register(Reviews)
admin.site.register(Comments)
admin.site.register(Book_list)
admin.site.register(Books_in_list)
admin.site.register(Reading_status)
admin.site.register(Favourites)
    