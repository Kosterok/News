import re
from django import template

register = template.Library()

BAD_WORDS = ['редиска', 'дурак', 'глупец', 'забияка']

@register.filter(name='censor')
def censor(value: str):
    if not isinstance(value, str):
        raise ValueError("Фильтр можно применять только к строкам")

    def replace_bad_word(match):
        word = match.group()
        return word[0] + '*' * (len(word) - 1)

    result = value
    for bad in BAD_WORDS:
        result = re.sub(rf'\b{bad}\b', replace_bad_word, result, flags=re.IGNORECASE)

    return result