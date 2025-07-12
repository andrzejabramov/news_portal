## Задание 9.1 (HW-03)

1. Создать двух пользователей (с помощью метода User.objects.create_user('username')).  
```commandline
User.objects.create_user('AndrzejVod')
User.objects.create_user('Ksiu')
```
![Users](https://github.com/andrzejabramov/news_portal/blob/master/img/1_Users.png)
2. Создать два объекта модели Author, связанные с пользователями. 
```commandline
from django.contrib.auth.models import User
from news.models import Author

# Получаем пользователей
user1 = User.objects.get(username='AndrzejVod')
user2 = User.objects.get(username='Ksiu')

# Создаём авторов
author1 = Author.objects.create(user=user1)
author2 = Author.objects.create(user=user2)

# Проверяем
print(Author.objects.all())
```
![Authors](https://github.com/andrzejabramov/news_portal/blob/master/img/2_Authors.png)
3. Добавить 4 категории в модель Category.  
```commandline
cat1 = Categoty.objects.create(name='Политика')
cat1 = Categoty.objects.create(name='Спорт')
cat1 = Categoty.objects.create(name='Наука')
cat1 = Categoty.objects.create(name='Семья')
```
![Categories](https://github.com/andrzejabramov/news_portal/blob/master/img/3_Categories.png)
4. Добавить 2 статьи и 1 новость.  
```commandline
post1 = Post.objects.create(author=author1, type='article', title='Статья 1', text='Текст статьи 1', rating=0)
post2 = Post.objects.create(author=author2, type='news', title='Новость 1', text='Текст новости 1', rating=0)
```
![PostNews](https://github.com/andrzejabramov/news_portal/blob/master/img/4_Posts.png)
5. Присвоить им категории (как минимум в одной статье/новости должно быть не меньше 2 категорий).  
```commandline
# Добавляем категории к постам
post1.categories.add(cat1, cat2)
post2.categories.add(cat1)
post3.categories.add(cat2, cat3)
```
![Cat_PostNews](https://github.com/andrzejabramov/news_portal/blob/master/img/5_News_PostCategory.png)
6. Создать как минимум 4 комментария к разным объектам модели Post (в каждом объекте должен быть как минимум один комментарий).  
```commandline
from news.models import Comment
from django.contrib.auth.models import User

# Получаем других пользователей или тех же авторов как пользователи
user3 = User.objects.get(username=' ZhdanDaniil')  # например, другой пользователь

comment1 = Comment.objects.create(post=post1, user=user1, text='Хорошая статья!', rating=2)
comment2 = Comment.objects.create(post=post1, user=user3, text='Не согласен.', rating=-1)
comment3 = Comment.objects.create(post=post3, user=user2, text='Отличная работа!', rating=5)
```
![Comments](https://github.com/andrzejabramov/news_portal/blob/master/img/6_Comments.png)
7. Применяя функции like() и dislike() к статьям/новостям и комментариям, скорректировать рейтинги этих объектов. 
```commandline
# Увеличиваем рейтинг статьи
post1.like()
post1.like()
post1.like()  # +3

# Уменьшаем рейтинг новости
post2.dislike()
post2.dislike()  # -2

# Обновляем объект из БД, чтобы увидеть изменения
post1.refresh_from_db()
post2.refresh_from_db()

print(f"Рейтинг статьи '{post1.title}': {post1.rating}")   # Ожидаем 3
print(f"Рейтинг новости '{post2.title}': {post2.rating}")   # Ожидаем -2

# Создаем комментарии
comment1 = Comment.objects.create(post=post1, user=user1, text='Хорошая статья!', rating=0)
comment2 = Comment.objects.create(post=post1, user=user2, text='Не согласен.', rating=0)

# Лайки и дизлайки
comment1.like()        # +1
comment2.dislike()     # -1

# Обновляем и выводим
comment1.refresh_from_db()
comment2.refresh_from_db()

print(f"Рейтинг комментария '{comment1.text[:20]}...': {comment1.rating}")  # 1
print(f"Рейтинг комментария '{comment2.text[:20]}...': {comment2.rating}")  # -1
```
![Like_Dislike](https://github.com/andrzejabramov/news_portal/blob/master/img/7_like_dislike.png)
8. Обновить рейтинги пользователей.  
```commandline
author1.update_rating()
author2.update_rating()

author1.refresh_from_db()
author2.refresh_from_db()

print(f"Рейтинг автора {author1.user.username}: {author1.rating}")
print(f"Рейтинг автора {author2.user.username}: {author2.rating}")
```
![Refresh](https://github.com/andrzejabramov/news_portal/blob/master/img/8_Change_rating.png)
9. Вывести username и рейтинг лучшего пользователя (применяя сортировку и возвращая поля первого объекта).  
```commandline
best_author = Author.objects.order_by('-rating').first()
print(f"Лучший пользователь: {best_author.user.username}, Рейтинг: {best_author.rating}")
```
10. Вывести дату добавления, username автора, рейтинг, заголовок и превью лучшей статьи, основываясь на лайках/дизлайках к этой статье. 
```commandline
best_post = Post.objects.order_by('-rating').select_related('author__user').first()

print(f"""
Дата добавления: {best_post.created_at}
Автор: {best_post.author.user.username}
Рейтинг: {best_post.rating}
Заголовок: {best_post.title}
Превью: {best_post.preview()}
""")
```
![Best_Post](https://github.com/andrzejabramov/news_portal/blob/master/img/9_10_Author_rating.png)
11. Вывести все комментарии (дата, пользователь, рейтинг, текст) к этой статье.
```commandline
best_post = Post.objects.order_by('-rating').select_related('author__user').first()

print(f"""
Дата добавления: {best_post.created_at}
Автор: {best_post.author.user.username}
Рейтинг: {best_post.rating}
Заголовок: {best_post.title}
Превью: {best_post.preview()}
""")
```
![Best_Comments](https://github.com/andrzejabramov/news_portal/blob/master/img/11_Comments_for_post.png)