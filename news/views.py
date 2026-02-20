# news/views.py
from django.views.generic import ListView, DetailView
from django_filters.views import FilterView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from datetime import datetime
from .models import Post
from .filters import PostFilter
from .forms import PostForm


class PostList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(type=Post.NEWS)


class PostDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'


class PostSearch(FilterView):
    model = Post
    template_name = 'news_search.html'
    context_object_name = 'news'
    filterset_class = PostFilter
    paginate_by = 10


class PostCreate(LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        # ← Устанавливаем автора из текущего пользователя
        post.author = self.request.user.author
        # ← Устанавливаем тип по URL
        if self.request.resolver_match.url_name == 'news_create':
            post.type = Post.NEWS
        elif self.request.resolver_match.url_name == 'article_create':
            post.type = Post.ARTICLE
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('news:post_detail', kwargs={'pk': self.object.pk})


class PostUpdate(LoginRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def get_success_url(self):
        return reverse_lazy('news:post_detail', kwargs={'pk': self.object.pk})


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news:post_list')

    def get_queryset(self):
        # ← Защита: удалять можно только свои посты
        return Post.objects.filter(author__user=self.request.user)
