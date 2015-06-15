from django import template

register = template.Library()


@register.inclusion_tag('articles/inclusion/tag_list.html')
def tag_list(tags):
    return {
        'tags': tags
    }
