# news/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, TemplateView
from django_filters.views import FilterView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.views import View
from news.models import Category, UserCategorySubscription
from django.urls import reverse_lazy
import time

from .models import Post, Comment  # ← Добавили импорт Comment
from .filters import PostFilter
from .forms import PostForm, CommentForm, CommentEditForm  # ← Добавили CommentEditForm


class PostList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news/news.html'
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
    template_name = 'news/new.html'
    context_object_name = 'new'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comment_set.all().order_by('-created_at')
        context['comment_form'] = CommentForm()
        return context


class PostSearch(FilterView):
    model = Post
    template_name = 'news/news_search.html'
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
    template_name = 'news/post_edit.html'

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
    template_name = 'news/post_edit.html'

    def get_queryset(self):
        return Post.objects.all()

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.author.user != self.request.user:
            raise PermissionDenied('❌ У вас отсутствуют права на редактирование данной публикации')
        return obj

    def get_success_url(self):
        return reverse_lazy('news:post_detail', kwargs={'pk': self.object.pk})


# class PostDelete(LoginRequiredMixin, DeleteView):
#     """
#     Удаление поста (новости/статьи).
#     Доступно только автору поста.
#     """
#     model = Post
#     template_name = 'post_delete.html'
#     success_url = reverse_lazy('news:post_list')
#
#     def get_queryset(self):
#         return Post.objects.all()
#
#     def dispatch(self, request, *args, **kwargs):
#         """Проверка прав до ДО обработки запроса"""
#         obj = self.get_object()
#         # Проверяем, является ли пользователь автором
#         if not request.user.is_authenticated or obj.author.user != request.user:
#             raise PermissionDenied("❌ У вас нет прав на удаление этой публикации")
#         return super().dispatch(request, *args, **kwargs)
#
#     def delete(self, request, *args, **kwargs):
#         """Логируем успешное удаление"""
#         obj = self.get_object()
#         response = super().delete(request, *args, **kwargs)
#         messages.success(request, f'✅ Публикация «{obj.title}» удалена')
#         return response


class PostDelete(LoginRequiredMixin, DeleteView):
    """
    Удаление поста (новости/статьи).
    Доступно только автору поста.
    """
    model = Post
    template_name = 'news/post_delete.html'
    success_url = reverse_lazy('news:post_list')
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.all()

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        # Проверка прав доступа
        if not self.request.user.is_authenticated:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Требуется авторизация")

        if obj.author.user != self.request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("❌ Вы не можете удалить чужую публикацию")

        return obj

    def post(self, request, *args, **kwargs):
        """Обрабатываем POST-запрос на удаление"""
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Удаление поста"""
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'✅ Публикация «{obj.title}» удалена')
        return response


class SubscribeToggleView(LoginRequiredMixin, View):
    """
    Переключает подписку пользователя на категорию.
    """

    def post(self, request, category_pk):
        action = request.POST.get('action', 'subscribe')
        subscribe = (action != 'unsubscribe')
        return self._toggle_subscription(request, category_pk, subscribe=subscribe)

    def get(self, request, category_pk):
        action = request.GET.get('action', 'subscribe')
        subscribe = (action != 'unsubscribe')
        return self._toggle_subscription(request, category_pk, subscribe=subscribe)

    def _toggle_subscription(self, request, category_pk, subscribe=True):
        category = get_object_or_404(Category, pk=category_pk)
        user = request.user

        if subscribe:
            sub, created = UserCategorySubscription.objects.get_or_create(
                user=user,
                category=category,
                defaults={'is_active': True}
            )
            if not created and not sub.is_active:
                sub.is_active = True
                sub.save()
            messages.success(
                request,
                f'✅ Вы подписаны на категорию «{category.name}». '
                f'Теперь вы будете получать уведомления о новых публикациях.'
            )
        else:
            try:
                sub = UserCategorySubscription.objects.get(user=user, category=category)
                sub.is_active = False
                sub.save()
                messages.success(
                    request,
                    f'🔕 Вы отписались от категории «{category.name}».'
                )
            except UserCategorySubscription.DoesNotExist:
                messages.info(request, f'Вы не были подписаны на «{category.name}».')

        redirect_url = request.META.get('HTTP_REFERER', reverse_lazy('news:post_list'))
        separator = '&' if '?' in redirect_url else '?'
        return redirect(f"{redirect_url}{separator}t={int(time.time())}")


class SubscriptionsListView(LoginRequiredMixin, TemplateView):
    """
    Страница управления подписками пользователя.
    """
    template_name = 'news/subscriptions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all().order_by('name')
        user_subscriptions = UserCategorySubscription.objects.filter(
            user=self.request.user
        ).values_list('category_id', flat=True)

        categories_with_status = []
        for cat in categories:
            categories_with_status.append({
                'category': cat,
                'is_subscribed': cat.id in user_subscriptions,
            })

        context['categories'] = categories_with_status
        return context

# =============================================================================
# КОММЕНТАРИИ: Функции для работы с комментариями
# =============================================================================

def post_detail(request, pk):
    """Страница публикации с комментариями"""
    post = get_object_or_404(Post, pk=pk)
    comments = post.comment_set.all().order_by('-created_at')
    comment_form = CommentForm()

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            messages.success(request, '✅ Комментарий добавлен!')
            return redirect('news:post_with_comments', pk=pk)

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'news/post_detail.html', context)


@login_required
def add_comment(request, pk):
    """Отдельный URL для добавления комментария"""
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            messages.success(request, '✅ Комментарий добавлен!')
            return redirect('news:post_with_comments', pk=pk)

    return redirect('news:post_with_comments', pk=pk)


@login_required
def edit_comment(request, pk):
    """Редактирование своего комментария"""
    comment = get_object_or_404(Comment, pk=pk)

    if comment.user != request.user:
        messages.error(request, '❌ Вы можете редактировать только свои комментарии.')
        return redirect('news:post_with_comments', pk=comment.post.pk)

    if request.method == 'POST':
        form = CommentEditForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, '✏️ Комментарий обновлён!')
            return redirect('news:post_with_comments', pk=comment.post.pk)

    form = CommentEditForm(instance=comment)
    return render(request, 'news/comment_edit.html', {'comment': comment, 'form': form})


@login_required
def delete_comment(request, pk):
    """Удаление своего комментария"""
    comment = get_object_or_404(Comment, pk=pk)

    if comment.user != request.user:
        messages.error(request, '❌ Вы можете удалять только свои комментарии.')
        return redirect('news:post_with_comments', pk=comment.post.pk)

    post_pk = comment.post.pk
    comment.delete()
    messages.success(request, '🗑️ Комментарий удалён!')
    return redirect('news:post_with_comments', pk=post_pk)


@login_required
def like_comment(request, pk):
    """Лайк комментария"""
    comment = get_object_or_404(Comment, pk=pk)
    comment.like()
    return redirect('news:post_with_comments', pk=comment.post.pk)


@login_required
def dislike_comment(request, pk):
    """Дизлайк комментария"""
    comment = get_object_or_404(Comment, pk=pk)
    comment.dislike()
    return redirect('news:post_with_comments', pk=comment.post.pk)

