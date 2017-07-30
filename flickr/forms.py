from django import forms
from .models import Search, Annotation


class SearchForm(forms.ModelForm):

    class Meta:
        model = Search
        exclude = []


class AnnotationForm(forms.ModelForm):

    class Meta:
        model = Annotation
        exclude = []
