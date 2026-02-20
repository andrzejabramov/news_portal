# news/templatetags/custom_filters.py
from django import template
import re

register = template.Library()


# ← Фильтр для пагинации (сохраняет параметры в URL)
@register.filter
def remove(value, arg):
    """Удаляет параметр из QUERY_STRING"""
    import urllib.parse
    params = urllib.parse.parse_qs(value)
    params.pop(arg, None)
    return urllib.parse.urlencode(params, doseq=True)


# ← Фильтр цензуры (заменяет плохие слова на *)
@register.filter
def censor(value):
    """Заменяет запрещённые слова на звёздочки"""
    if not value:
        return value

    # Список слов для цензуры (добавляй свои)
    bad_words = ['дурак', 'идиот', 'редиска', 'болван']

    result = value
    for word in bad_words:
        # Замена: оставляем первую и последнюю букву, остальные *
        if len(word) > 2:
            censored = word[0] + '*' * (len(word) - 2) + word[-1]
        else:
            censored = '*' * len(word)
        # Регексп для замены с учётом регистра
        result = re.sub(
            re.escape(word),
            censored,
            result,
            flags=re.IGNORECASE
        )

    return result