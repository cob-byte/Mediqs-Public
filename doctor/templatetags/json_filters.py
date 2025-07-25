from django import template
import json

register = template.Library()

@register.filter
def get_value(dictionary, key):
    if isinstance(dictionary, str):
        dictionary = json.loads(dictionary)
    return dictionary.get(key)
