from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост и еще-что для 15 символов',
        )

    def test_post_model_has_correct_object_names(self):
        """Проверяем, что у модели корректно работает __str__."""
        expected_post_name = PostModelTest.post.text[
            :settings.SYMBOL_RESTRICTION_FOR_POST_NAME
        ]
        self.assertEqual(expected_post_name, str(PostModelTest.post))

    def test_verbose_name_post(self):
        """Проверяем verbose_name объекта post"""
        post = PostModelTest.post
        field_verboses_post = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_post_title_help_text(self):
        """Проверяем help_text модели post"""
        post = PostModelTest.post

        self.assertEqual(
            post._meta.get_field('text').help_text, 'Введите текст поста'
        )

    def test_group_title_help_text(self):
        """Проверяем help_text модели group"""
        post = Post.objects.create(
            author=PostModelTest.user,
            text='Тестовый пост и еще-что для 15 символов',
        )

        self.assertEqual(
            post._meta.get_field('group').help_text,
            'Группа, к которой будет относиться пост'
        )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа и еще что-то',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_model_has_correct_object_names(self):
        """Проверяем, что у модели корректно работает __str__."""
        expected_group_name = GroupModelTest.group.title
        self.assertEqual(expected_group_name, str(GroupModelTest.group))

    def test_verbose_name_group(self):
        """Проверяем поля verbose_name объекта group"""
        group = GroupModelTest.group
        field_verboses_group = {
            'title': 'Название',
            'slug': 'Ссылка',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses_group.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)
