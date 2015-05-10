# Create your views here.
#from django.utils.text import slugify
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden
#from django.contrib.auth.decorators import login_required
#from django.shortcuts import get_object_or_404, render_to_response
#from django.core.paginator import Paginator, PageNotAnInteger
#from django.contrib.auth.models import User
#from django.core.urlresolvers import reverse
#from django.contrib import messages
#from django.views.decorators.cache import cache_page, never_cache
from articles.models import Article
from django.template import RequestContext, loaderne
from django.conf import settings

def home(request):
    page_size = 10
    t = loader.get_template('home.html')
    c = RequestContext(request, {
        'articles': Article.objects.filter(published=True).filter(is_page=False).order_by('-created')[:page_size],
        'header_image': getattr(settings, 'homepage_image', None),
        'homepage': True,
        })
    return HttpResponse(t.render(c))
