from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserEditForm

User = get_user_model()


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


from django.shortcuts import get_object_or_404

def post_detail(request, id):
    post = get_object_or_404(Post, id=id)
    
    if not post.is_published or post.pub_date > timezone.now() or not post.category.is_published:
        if request.user != post.author:
            raise Http404("Пост не найден") 
    
    comments = post.comments.order_by('created_at')
    
    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'form': CommentForm(),
    })


@login_required
def add_comment(request, id):
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        raise Http404("Пост не найден")

    if not post.is_published or post.pub_date > timezone.now() or not post.category.is_published:
        if request.user != post.author:
            raise Http404("Пост не найден")
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    
    return redirect('blog:post_detail', id=post.id)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # post.pub_date = timezone.now()  ← УДАЛИТЬ ЭТУ СТРОКУ
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def post_edit(request, id):
    post = get_object_or_404(Post, id=id)
    
    if post.author != request.user:
        return redirect('blog:post_detail', id=post.id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post.id)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/create.html', {'form': form})


@login_required
def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    
    if post.author != request.user:
        return redirect('blog:post_detail', id=post.id)
    
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    
    return render(request, 'blog/confirm_delete.html', {'object': post})


def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_published=True)
    
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
        'page_obj': page_obj,
    })


def profile(request, username):
    user = get_object_or_404(User, username=username)
    
    if request.user == user:
        posts = Post.objects.filter(author=user)
    else:
        posts = Post.objects.filter(
            author=user,
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )
    
    posts = posts.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/profile.html', {
        'profile': user,
        'page_obj': page_obj,
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserEditForm(instance=request.user)
    
    return render(request, 'blog/edit_profile.html', {'form': form})


@login_required
def edit_comment(request, id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=id)
    
    if comment.author != request.user:
        return redirect('blog:post_detail', id=id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=id)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'blog/comment_form.html', {
        'form': form,
        'comment': comment,
        'post': comment.post,
    })


@login_required
def delete_comment(request, id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=id)

    if comment.author != request.user:
        return redirect('blog:post_detail', id=id)
    
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=id)
    
    return render(request, 'blog/confirm_delete.html', {'object': comment})

def registration(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'registration/registration_form.html', {'form': form})