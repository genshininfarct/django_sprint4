from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import Http404
from django.core.paginator import Paginator
from django.db.models import Count

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, RegisterForm, ProfileForm

import logging
logger = logging.getLogger(__name__)


def index(request):
    posts = (
        Post.objects
        .filter(is_published=True, pub_date__lte=timezone.now(),
                category__is_published=True)
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if not post.is_published or not post.category.is_published or post.pub_date > timezone.now():
        if not request.user.is_authenticated or request.user != post.author:
            raise Http404

    comments = post.comments.all().order_by('created_at')
    form = CommentForm()
    return render(request, 'blog/detail.html',
                  {'post': post, 'comments': comments, 'form': form})


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug, is_published=True)
    posts = (
        Post.objects
        .filter(category=category, is_published=True,
                pub_date__lte=timezone.now())
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/category.html',
                  {'category': category, 'page_obj': page_obj})


def profile(request, username):
    User = get_user_model()
    user = get_object_or_404(User, username=username)

    if request.user == user:
        posts = user.posts.all()
    else:
        posts = user.posts.filter(is_published=True,
                                  pub_date__lte=timezone.now(),
                                  category__is_published=True)

    posts = posts.annotate(comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'blog/profile.html',
                  {'profile': user, 'page_obj': page_obj})


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'registration/registration_form.html',
                  {'form': form})


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        if post.pub_date is None:
            post.pub_date = timezone.now()
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)
    return render(request, 'blog/create.html', {'form': form, 'post': post})


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return redirect('blog:post_detail', post_id=post.id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', post_id=post.id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'GET':
        form = CommentForm(instance=comment)
        return render(request, 'blog/comment.html', {
            'form': form,
            'comment': comment,
            'is_edit': True
        })

    elif request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
        return render(request, 'blog/comment.html', {
            'form': form,
            'comment': comment,
            'is_edit': True
        })

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'GET':
        return render(request, 'blog/comment.html', {
            'comment': comment,
            'is_edit': False
        })

    elif request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_profile(request, username):
    """Редактирование профиля пользователя"""
    logger.debug(f"profile_edit called for user: {username}")

    User = get_user_model()
    user = get_object_or_404(User, username=username)
    logger.debug(f"Found user: {user.username}, requesting user: {request.user.username}")

    # Проверяем, что пользователь редактирует свой профиль
    if request.user != user:
        logger.warning(f"User {request.user.username} tried to edit {user.username}'s profile")
        return redirect('blog:profile', username=username)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        logger.debug(f"POST request, form valid: {form.is_valid()}")
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=username)
    else:
        form = ProfileForm(instance=user)
        logger.debug(f"GET request, form created with fields: {form.fields.keys()}")

    # Важно: используем шаблон blog/user.html
    return render(request, 'blog/user.html', {'form': form})
