# news/forms.py
from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # ← Исключаем поле 'type' (устанавливается автоматически)
        # ← Исключаем 'author' (устанавливается из текущего пользователя)
        # ← Исключаем 'rating' (автоматическое)
        fields = ['title', 'text', 'categories']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Заголовок'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Текст публикации'
            }),
            'categories': forms.CheckboxSelectMultiple(),
        }

# =============================================================================
# ФОРМА КОММЕНТАРИЯ
# =============================================================================

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ваш комментарий...',
                'style': 'resize: vertical;'  # Чтобы можно было растягивать по вертикали
            })
        }


class CommentEditForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'style': 'resize: vertical;'
            })
        }