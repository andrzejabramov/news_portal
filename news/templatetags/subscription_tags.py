# news/templatetags/subscription_tags.py

from django import template
from news.models import UserCategorySubscription

register = template.Library()


@register.simple_tag(takes_context=True)
def check_subscription(context, user_id, category_id):
    """
    Проверяет подписку по ID.
    takes_context=True помогает Django понять, что тег зависит от контекста.
    """
    if not user_id or not category_id:
        return False
    
    # Принудительно делаем свежий запрос к БД (без кэша)
    result = UserCategorySubscription.objects.filter(
        user_id=user_id,
        category_id=category_id,
        is_active=True
    ).exists()
    
    return result
