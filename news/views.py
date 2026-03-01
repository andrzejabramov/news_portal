# news/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied  # ← Новый импорт
from django.views.generic import ListView, DetailView
from django_filters.views import FilterView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_author'] = self.request.user.groups.filter(name='authors').exists()
        return context


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


class PostCreate(
    PermissionRequiredMixin,
    LoginRequiredMixin,
    CreateView,
):
    permission_required = 'news.add_post'
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user.author
        if self.request.resolver_match.url_name == 'news_create':
            post.type = Post.NEWS
        elif self.request.resolver_match.url_name == 'article_create':
            post.type = Post.ARTICLE
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('news:post_detail', kwargs={'pk': self.object.pk})


class PostUpdate(
    PermissionRequiredMixin,
    LoginRequiredMixin,
    UpdateView
):
    permission_required = 'news.change_post'
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def get_queryset(self):
        # Возвращаем ВСЕ посты, чтобы Django мог найти объект по PK
        return Post.objects.all()

    def get_object(self, queryset=None):
        # Получаем объект стандартным способом
        obj = super().get_object(queryset)
        # Проверяем, что это пост текущего пользователя
        if obj.author.user != self.request.user:
            # ← Вместо 404 показываем понятную ошибку
            raise PermissionDenied('❌ У вас отсутствуют права на редактирование данной публикации')
        return obj

    def get_success_url(self):
        return reverse_lazy('news:post_detail', kwargs={'pk': self.object.pk})


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news:post_list')

    def get_queryset(self):
        # Возвращаем ВСЕ посты, чтобы Django мог найти объект по PK
        return Post.objects.all()

    def get_object(self, queryset=None):
        # Получаем объект стандартным способом
        obj = super().get_object(queryset)
        # Проверяем, что это пост текущего пользователя
        if obj.author.user != self.request.user:
            # ← Вместо 404 показываем понятную ошибку
            raise PermissionDenied('❌ У вас отсутствуют права на удаление данной публикации')
        return obj