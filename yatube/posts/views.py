from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.conf import settings
from django.db.models import QuerySet

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


def paginator_func(some_query: QuerySet,
                   request: HttpRequest,
                   list_per_page:
                   int = settings.SORTED_VALUES_AMOUNT,) -> Paginator:
    """To return Paginator object"""
    paginator: Paginator = Paginator(some_query, list_per_page)
    page_number: int = request.GET.get('page')
    page_obj: Paginator = paginator.get_page(page_number)
    return page_obj


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.select_related('author', 'group').all()
    page_obj = paginator_func(some_query=post_list,
                              request=request,)
    context = {'page_obj': page_obj, }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author',).all()
    page_obj = paginator_func(some_query=post_list,
                              request=request,)
    context = {'group': group,
               'page_obj': page_obj, }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group').all()
    page_obj = paginator_func(some_query=post_list,
                              request=request,)

    if request.user.is_authenticated and Follow.objects.filter(
            user=request.user,
            author=author).exists():
        following = True
    else:
        following = False

    context = {'author': author,
               'page_obj': page_obj,
               'following': following}
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post.objects.select_related('author'), pk=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {'post': post,
               'comments': comments,
               'form': form,
               }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    context = {'form': form}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {'form': form,
               'is_edit': True, }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related('author', 'group')
    page_obj = paginator_func(some_query=posts,
                              request=request,)
    context = {'page_obj': page_obj, }

    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)

    if request.user.username != username:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect(
        'posts:profile',
        author
    )


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)

    subscription = author.following.filter(user=request.user)

    subscription.delete()
    return redirect(
        'posts:profile',
        author
    )
