# news/admin.py
from django.contrib import admin
from .models import Author, Category, Post, PostCategory, Comment

# ← Регистрируем все модели, чтобы они появились в админке
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(PostCategory)
admin.site.register(Comment)

# Register your models here.
