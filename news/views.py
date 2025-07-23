from django.views.generic import ListView, DetailView
from .models import Post


class PostList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news.html'
    context_object_name = 'news'

    def get_queryset(self):
        return Post.objects.filter(type=Post.NEWS)


class PostDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'

