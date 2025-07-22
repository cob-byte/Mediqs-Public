from django import template
from django.conf import settings

register = template.Library()

@register.filter
def adjust_image_url(url):
    if url.startswith("/static/"):
        return url
    return f"/static{url}"