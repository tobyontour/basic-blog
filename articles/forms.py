from django import forms
from .models import Article, ArticleImage

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title','body','subheading', 'image', 'slug', 'published', 'is_page')

class ArticleImageForm(forms.ModelForm):
    class Meta:
        model = ArticleImage
        fields = ('title', 'image')

