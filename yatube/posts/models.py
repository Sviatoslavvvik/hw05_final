from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Ссылка')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)
        verbose_name_plural = 'Группы постов'


class Post(CreatedModel):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Введите текст поста',)

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор',
                               )
    group = models.ForeignKey(Group,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              verbose_name='Группа',
                              help_text=('Группа, '
                                         'к которой будет относиться пост'))
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:settings.SYMBOL_RESTRICTION_FOR_POST_NAME]

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = 'Посты'


class Comment(CreatedModel):
    post = models.ForeignKey(Post,
                             blank=True,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Комментарий',
                             help_text=('Комментарий под '
                                        'постом'))
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор',
                               )
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Введите текст комментария',)

    def __str__(self):
        return self.text[:settings.SYMBOL_RESTRICTION_FOR_POST_NAME]

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(
                    user=models.F('author')
                ), name='user=author'),
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='users follow on uniq authors'
            )
        ]
