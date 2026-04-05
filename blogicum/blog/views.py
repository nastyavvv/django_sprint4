from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserEditForm

def index(request):
    posts = Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})

def post_detail(request, id):
    form = CommentForm(request.POST or None)

    comments = post.comments.order_by('created_at')

    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', id=post.id)

@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/create.html', {'form': form})

@login_required
def post_edit(request, id):
    post = get_object_or_404(Post, id=id)

    if post.author != request.user:
        return HttpResponseForbidden("Нет доступа")

    form = PostForm(request.POST or None, instance=post)

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=post.id)

    return render(request, 'blog/create.html', {'form': form})

@login_required
def post_delete(request, id):
    post = get_object_or_404(Post, id=id)

    if post.author != request.user:
        return HttpResponseForbidden("Нет доступа")

    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')

    return render(request, 'blog/post_confirm_delete.html', {
        'object': post
    })

def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    posts = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj
    })

def registration(request):
    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('login')

    return render(request, 'registration/registration_form.html', {'form': form})

User = get_user_model()

def profile(request, username):
    user = get_object_or_404(User, username=username)

    if request.user == user:
        posts = Post.objects.filter(author=user)
    else:
        posts = Post.objects.filter(
            author=user,
            is_published=True,
            pub_date__lte=timezone.now()
        )

    posts = posts.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/profile.html', {
        'profile': user,
        'page_obj': page_obj
    })

@login_required
def edit_comment(request, id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        return HttpResponseForbidden("Нет доступа")

    form = CommentForm(request.POST or None, instance=comment)

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=id)

    return render(request, 'blog/comment_form.html', {'form': form})


@login_required
def delete_comment(request, id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        return HttpResponseForbidden("Нет доступа")

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=id)

    return render(request, 'blog/post_confirm_delete.html', {
        'object': comment
    })

@login_required
def edit_profile(request):
    form = UserEditForm(
        request.POST or None,
        instance=request.user
    )

    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/edit_profile.html', {'form': form})