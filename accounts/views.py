from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template import RequestContext, Context, loader
from django import forms
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinLengthValidator
from django.views.decorators.cache import never_cache

class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(label="Password", min_length=5,
        widget=forms.PasswordInput)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        f = self.fields.get('username')
        f.validators.append(MinLengthValidator(3))

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(
            'A user with that email already exists',
            code='duplicate_email',
        )

@never_cache
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save()
            # At this point, user is a User object that has already been saved
            # to the database. You can continue to change its attributes
            # if you want to change other fields.
            if form.cleaned_data['first_name']:
                user.first_name = form.cleaned_data['first_name']
            if form.cleaned_data['last_name']:
                user.last_name = form.cleaned_data['last_name']
            user.save()
            return HttpResponseRedirect(reverse('login'))
    else:
        form = RegistrationForm()

    template = loader.get_template('registration/register_form.html')
    context = {
        'form': form,
    }

    return render(request, 'registration/register_form.html', context)

@login_required()
@never_cache
def profile(request):
    return render(request, 'registration/profile.html', {})

@never_cache
def public_profile(request, username):
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist, e:
        return HttpResponseNotFound('No such user')

    context = {
        'username': profile_user.username
    }
    return render(request, 'registration/public_profile.html', context)
