## Задание 9.1 (HW-03)

1. Создать двух пользователей (с помощью метода User.objects.create_user('username')).  
![Users](https://github.com/andrzejabramov/news_portal/blob/master/img/1_Users.png)
2. Создать два объекта модели Author, связанные с пользователями. 
![Authors](https://github.com/andrzejabramov/news_portal/blob/master/img/2_Authors.png)
3. Добавить 4 категории в модель Category.  
![Categories](https://github.com/andrzejabramov/news_portal/blob/master/img/3_Categories.png)
4. Добавить 2 статьи и 1 новость.  
![PostNews](https://github.com/andrzejabramov/news_portal/blob/master/img/4_Posts.png)
5. Присвоить им категории (как минимум в одной статье/новости должно быть не меньше 2 категорий).  
![Cat_PostNews](https://github.com/andrzejabramov/news_portal/blob/master/img/5_News_PostCategory.png)
6. Создать как минимум 4 комментария к разным объектам модели Post (в каждом объекте должен быть как минимум один комментарий).  
![Comments](https://github.com/andrzejabramov/news_portal/blob/master/img/6_Comments.png)
7. Применяя функции like() и dislike() к статьям/новостям и комментариям, скорректировать рейтинги этих объектов.  
![Like_Dislike](https://github.com/andrzejabramov/news_portal/blob/master/img/7_like_dislike.png)
8. Обновить рейтинги пользователей.  
![Refresh](https://github.com/andrzejabramov/news_portal/blob/master/img/8_Change_rating.png)
9. Вывести username и рейтинг лучшего пользователя (применяя сортировку и возвращая поля первого объекта).  

10. Вывести дату добавления, username автора, рейтинг, заголовок и превью лучшей статьи, основываясь на лайках/дизлайках к этой статье. 
![Best_Post](https://github.com/andrzejabramov/news_portal/blob/master/img/9_10_Author_rating.png)
11. Вывести все комментарии (дата, пользователь, рейтинг, текст) к этой статье.
![Best_Comments](https://github.com/andrzejabramov/news_portal/blob/master/img/11_Comments_for_post.png)


