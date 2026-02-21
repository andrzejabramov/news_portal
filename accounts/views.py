from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages


@login_required
def become_author(request):
    """Добавляет текущего пользователя в группу authors"""
    if request.method == 'POST':
        authors_group, created = Group.objects.get_or_create(name='authors')
        request.user.groups.add(authors_group)
        messages.success(request, 'Теперь вы можете создавать публикации!')
        return redirect('news:post_list')

    return render(request, 'accounts/become_author.html')
