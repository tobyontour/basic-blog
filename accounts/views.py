from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template import RequestContext, Context, loader
from django.contrib.auth.models import User
from django import forms
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page, never_cache


class RegistrationForm(forms.Form):
    username = forms.RegexField(r'^[a-z]+$', min_length=2, max_length=8)
    email = forms.EmailField()
    password = forms.CharField(min_length=5, widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        return cleaned_data

@never_cache
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                try:
                    existing_user = User.objects.get(email=form.cleaned_data['email'])
                except Exception, e:
                    # Doesn't exist
                    pass
                else:
                    raise Exception("User exists")
                # Create user
                user = User.objects.create_user(
                    form.cleaned_data['username'],
                    form.cleaned_data['email'],
                    form.cleaned_data['password']
                )

                # At this point, user is a User object that has already been saved
                # to the database. You can continue to change its attributes
                # if you want to change other fields.
                #user.last_name = 'Lennon'
                #user.save()
                return HttpResponseRedirect(reverse('login'))
            except Exception, e:
                messages.add_message(request, messages.ERROR, 'Username or email exists.')

    else:
        form = RegistrationForm()
    template = loader.get_template('registration/register_form.html')
    context = RequestContext(request, {
        'form': form,
    })

    return HttpResponse(template.render(context))

@login_required()
@never_cache
def profile(request):
    template = loader.get_template('registration/profile.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))

@login_required()
@never_cache
def public_profile(request, username):
    template = loader.get_template('registration/public_profile.html')

    try:
        profile_user = User.objects.get(username=username)
    except DoesNotExist:
        return HttpResponseNotFound('No such user')

    context = RequestContext(request, {
        'username': profile_user.username
    })
    return HttpResponse(template.render(context))
