from django import template
from django.template import loader, Context, Library

register = template.Library()

@register.inclusion_tag('articles/inclusion/tag_list.html')
def tag_list(tags):
    return {
        'tags': tags
    }
