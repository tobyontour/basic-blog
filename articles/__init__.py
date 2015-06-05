from articles.models import Article
from django.core.cache import caches
from django.db.models.signals import post_save, post_delete

cache = caches['default']

def menu_for_pages(request):
    '''
    Provides a list of static pages for the menu
    '''
    data = cache.get('menu_for_pages')
    if data is None:
        data = {
            'menu_pages': Article.objects.filter(published=True).filter(is_page=True).exclude(slug__in=['home','articles'])
        }
        cache.set('menu_for_pages', data, 300)
    return data

def articles_changed(sender, **kwargs):
    '''
    Flushes the page cache when a page is saved
    '''
    instance = kwargs['instance']
    if instance.published and instance.is_page and instance.slug not in ['home', 'articles']:
        cache.delete('menu_for_pages')

post_save.connect(articles_changed, sender=Article)
post_delete.connect(articles_changed, sender=Article)
