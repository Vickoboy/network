from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from .models import User, Post, Like, Follow, Comment

# ---------------- auth views (unchanged behaviour) ----------------
def index(request):
    # Show all posts (paginated)
    posts = Post.objects.order_by("-timestamp").all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    liked_post_ids = set()
    if request.user.is_authenticated:
        liked_post_ids = set(request.user.likes.values_list("post_id", flat=True))

    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "liked_post_ids": liked_post_ids
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {"message": "Invalid username and/or password."})
    return render(request, "network/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {"message": "Passwords must match."})
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {"message": "Username already taken."})
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "network/register.html")

# ---------------- posts API and page logic ----------------

@login_required
@require_http_methods(["POST"])
def create_post(request):
    """
    Create a new post via JSON (AJAX). Expects JSON: {"content": "..." }
    Returns created post data JSON.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    content = data.get("content", "").strip()
    if not content:
        return JsonResponse({"error": "Post content cannot be empty."}, status=400)

    post = Post.objects.create(author=request.user, content=content)
    return JsonResponse({
        "message": "Post created.",
        "post": {
            "id": post.id,
            "author": post.author.username,
            "content": post.content,
            "timestamp": post.timestamp.strftime("%Y-%m-%d %H:%M"),
            "likes": post.likes_count()
        }
    }, status=201)

@login_required
@require_http_methods(["PUT"])
def edit_post(request, post_id):
    """
    Edit a post's content. Only post author can edit.
    Expects JSON: {"content": "..."}
    """
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return HttpResponseForbidden("You cannot edit another user's post.")
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    new_content = data.get("content", "").strip()
    if not new_content:
        return JsonResponse({"error": "Content cannot be empty."}, status=400)

    post.content = new_content
    post.save()
    return JsonResponse({"message": "Post updated.", "content": post.content})

@login_required
@require_http_methods(["PUT"])
def toggle_like(request, post_id):
    """
    Toggle like for a post by current user. Returns liked boolean & new like count.
    """
    post = get_object_or_404(Post, pk=post_id)
    existing = Like.objects.filter(user=request.user, post=post)
    if existing.exists():
        existing.delete()
        liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        liked = True
    return JsonResponse({"liked": liked, "likes_count": post.likes_count()})

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    followers_count = profile_user.followers_set.count()
    following_count = profile_user.following_set.count()

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, followed=profile_user).exists()

    liked_post_ids = set()
    if request.user.is_authenticated:
        liked_post_ids = set(request.user.likes.values_list("post_id", flat=True))

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "page_obj": page_obj,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "liked_post_ids": liked_post_ids
    })

@login_required
@require_http_methods(["POST"])
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)

    if target == request.user:
        return JsonResponse({"error": "You cannot follow yourself."}, status=400)

    existing = Follow.objects.filter(follower=request.user, followed=target)
    if existing.exists():
        existing.delete()
        following = False
    else:
        Follow.objects.create(follower=request.user, followed=target)
        following = True

    followers_count = Follow.objects.filter(followed=target).count()
    return JsonResponse({"following": following, "followers_count": followers_count})

@login_required
def following_posts(request):
    followed_ids = request.user.following_set.values_list("followed_id", flat=True)
    posts = Post.objects.filter(author_id__in=followed_ids).order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    liked_post_ids = set(request.user.likes.values_list("post_id", flat=True))
    return render(request, "network/following.html", {
        "page_obj": page_obj,
        "liked_post_ids": liked_post_ids
    })

@login_required
@require_POST
def create_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    data = json.loads(request.body)
    content = data.get("content", "").strip()
    if not content:
        return JsonResponse({"error": "Comment cannot be empty."}, status=400)
    comment = Comment.objects.create(post=post, author=request.user, content=content)
    return JsonResponse({
        "author": comment.author.username,
        "content": comment.content,
        "timestamp": comment.timestamp.strftime("%Y-%m-%d %H:%M"),
    }, status=201)

@require_POST
@csrf_exempt
def post_comment(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=403)

    try:
        data = json.loads(request.body)
        content = data.get("content", "").strip()
        if not content:
            return JsonResponse({"error": "Empty comment."}, status=400)

        post = Post.objects.get(pk=post_id)
        comment = Comment.objects.create(post=post, author=request.user, content=content)

        return JsonResponse({
            "message": "Comment added successfully.",
            "author": request.user.username,
            "content": comment.content,
            "timestamp": comment.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)