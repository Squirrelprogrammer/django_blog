from typing import Type, Sequence

from django.http import HttpRequest, HttpResponse
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.serializers import BaseSerializer

from blog.forms import PostForm
from blog.models import Post
from blog.serializers import PostsSerializer


class PostsViewSet(viewsets.ModelViewSet):
    queryset: QuerySet = Post.objects.all()
    serializer_class: Type[PostsSerializer]  = PostsSerializer
    permission_classes: Sequence[Type[permissions.BasePermission]] = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer: BaseSerializer) -> None:
        if self.request.user.is_authenticated:
            serializer.save(
                author=self.request.user,
                created_date=timezone.now()
            )

    def perform_update(self, serializer: BaseSerializer) -> None:
        if self.request.user.is_authenticated:
            serializer.save(
                author=self.request.user,
                published_date=timezone.now()
            )


def post_list(request: HttpRequest) -> HttpResponse:
    posts: QuerySet[Post] = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    post: Post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})
