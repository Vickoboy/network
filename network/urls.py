from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),                           # All posts
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API endpoints and pages
    path("posts/create", views.create_post, name="create_post"),   # POST (JSON)
    path("posts/<int:post_id>/edit", views.edit_post, name="edit_post"),   # PUT (JSON)
    path("posts/<int:post_id>/like", views.toggle_like, name="toggle_like"), # PUT
    path("profile/<str:username>", views.profile, name="profile"),
    path("profile/<str:username>/follow", views.toggle_follow, name="toggle_follow"), # POST (AJAX)
    path("following", views.following_posts, name="following_posts"),
    path('posts/<int:post_id>/comment', views.post_comment, name='post_comment')
]
