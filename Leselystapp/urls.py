from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "Leselystapp"

urlpatterns = [
    path("", views.home, name="home"),
    path("books/", views.book_list, name="book_list"),
    path("books/<int:book_id>/", views.book_detail, name="book_detail"),
    path("authors/", views.author_list, name="author_list"),
    path("authors/<int:author_id>/", views.author_detail, name="author_detail"),
    path("signup/", views.signup, name="signup"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("profile/<str:username>/follow/", views.toggle_follow, name="toggle_follow"),
    path("profile/<str:username>/recommend/", views.recommend_book, name="recommend_book"),
    path("recommendations/", views.recommendations, name="recommendations"),
    path("recommendations/<int:rec_id>/read/", views.mark_recommendation_read, name="mark_recommendation_read"),
    path("challenge/set/", views.set_challenge, name="set_challenge"),
    path("books/<int:book_id>/add_review/", views.add_review, name="add_review"),
    path("reviews/<int:review_id>/add_comment/", views.add_comment, name="add_comment"),
    path("books/<int:book_id>/toggle_favourite/", views.toggle_favourite, name="toggle_favourite"),
    path("books/<int:book_id>/set_reading_status/", views.set_reading_status, name="set_reading_status"),
    path("books/<int:book_id>/add_to_list/", views.add_to_list, name="add_to_list"),
    path("my_lists/", views.my_lists, name="my_lists"),
    path("my_lists/create/", views.create_list, name="create_list"),
    path("my_lists/<int:list_id>/", views.list_detail, name="list_detail"),
    path("my_lists/<int:list_id>/edit/", views.edit_list, name="edit_list"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("settings/", views.account_settings, name="account_settings"),
    path("discussions/", views.discussions, name="discussions"),
    path("discussions/create/", views.create_discussion, name="create_discussion"),
    path("discussions/<int:discussion_id>/", views.discussion_detail, name="discussion_detail"),
    path("discussions/<int:discussion_id>/reply/", views.add_reply, name="add_reply"),
    path("search/", views.search, name="search"),
]