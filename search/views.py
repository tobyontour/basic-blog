from django.views.decorators.csrf import csrf_exempt
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from haystack.generic_views import SearchView
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet

class SiteSearchView(SearchView):
    template_name = 'search/search.html'
    queryset = SearchQuerySet()
    form_class = SearchForm

    @csrf_exempt
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].helper = FormHelper()
        context['form'].helper.form_class = 'form-horizontal'
        context['form'].helper.add_input(Submit('Search', 'search'))
        context['form'].helper.disable_csrf = True
        return context
