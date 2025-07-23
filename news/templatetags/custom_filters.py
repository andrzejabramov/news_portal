from django import template
import re

register = template.Library()

# Список нежелательных слов
BAD_WORDS = {
    'редиска',
    'дурак',
    'идиот',
    # добавьте свои слова
}

@register.filter(name='censor')
def censor(value):
    """
    Заменяет буквы нежелательных слов на '*'.
    """
    if not isinstance(value, str):
        return value

    for word in BAD_WORDS:
        # Игнорируем регистр, заменяем каждую букву слова на '*'
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        def replace_func(match):
            return match.group().replace(match.group(), '*' * len(match.group()))
        value = pattern.sub(replace_func, value)

    return value