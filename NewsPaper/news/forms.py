from django import forms
from django.core.exceptions import ValidationError
from .models import Post
class PostForm(forms.ModelForm):
    text = forms.CharField(min_length=20)
    class Meta:
       model = Post
       fields = ['categories',
                 'title',
                 'text',
                 'author']
       labels = {
           'categories': 'Категория',
           'title': 'Заголовок',
           'text': 'Текст',
           'author': 'Автор',
       }

       def clean(self):
           cleaned_data = super().clean()
           text = cleaned_data.get("text")
           title = cleaned_data.get("title")
           if title == text:
               raise ValidationError(
                   "Текст статьи не должен быть идентичным названию."
               )
           return cleaned_data