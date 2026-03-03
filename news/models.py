from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        # Суммарный рейтинг статей автора * 3
        post_rating = self.post_set.aggregate(total=Sum('rating'))['total'] or 0
        total_post_rating = post_rating * 3

        # Рейтинг комментариев пользователя как автора
        comment_rating_author = Comment.objects.filter(user=self.user).aggregate(total=Sum('rating'))['total'] or 0

        # Рейтинг комментариев к статьям автора
        comment_rating_posts = Comment.objects.filter(post__author=self).aggregate(total=Sum('rating'))['total'] or 0

        # Обновляем общий рейтинг автора
        self.rating = total_post_rating + comment_rating_author + comment_rating_posts
        self.save()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    ARTICLE = 'article'
    NEWS = 'news'
    POST_TYPES = (
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    )

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = models.CharField(choices=POST_TYPES, max_length=7)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + '...' if len(self.text) > 124 else self.text

    def __str__(self):
        return f"{self.type}, {self.created_at}, {self.title}, {self.text}, {self.rating}, {self.author}"


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.post.title} - {self.category.name}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f"Комментарий от {self.user.username} к {self.post.title}"


# =============================================================================
# ПОДПИСКИ ПОЛЬЗОВАТЕЛЕЙ НА КАТЕГОРИИ
# =============================================================================

class UserCategorySubscription(models.Model):
    """
    Подписка пользователя на категорию новостей.

    Пользователь может подписаться на одну категорию только один раз.
    При публикации новой статьи в подписанной категории пользователь
    получает уведомление на email.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='category_subscriptions',
        verbose_name='Пользователь'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Категория'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна',
        help_text='Если снято — пользователь не получает уведомления, но подписка сохраняется'
    )

    class Meta:
        verbose_name = 'Подписка на категорию'
        verbose_name_plural = 'Подписки на категории'
        unique_together = ('user', 'category')  # Защита от дублей
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        status = '✓' if self.is_active else '✗'
        return f"{status} {self.user.username} → {self.category.name}"

    def unsubscribe(self):
        """Мягкая отписка: деактивирует подписку без удаления"""
        self.is_active = False
        self.save()
        return True