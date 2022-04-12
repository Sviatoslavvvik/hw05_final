from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings

from ..models import Group, Post, Comment

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
            'group': 'Группа',
            'image': 'Картинка'
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


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.comment_author = User.objects.create_user(username='mrZ')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост и еще-что для 15 символов',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.comment_author,
            text='Тестовый коммент и еще-что для 15 символов',
        )

    def test_comment_model_has_correct_object_names(self):
        """Проверяем, что у модели корректно работает __str__."""
        expected_comment_name = CommentModelTest.comment.text[
            :settings.SYMBOL_RESTRICTION_FOR_POST_NAME
        ]
        self.assertEqual(expected_comment_name, str(CommentModelTest.comment))

    def test_verbose_name_comment(self):
        """Проверяем поля verbose_name объекта comment"""
        comment = CommentModelTest.comment
        field_verboses_comment = {
            'post': 'Комментарий',
            'author': 'Автор',
            'text': 'Текст комментария',
        }
        for field, expected_value in field_verboses_comment.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_group_title_help_text(self):
        """Проверяем help_text модели comment"""
        field_help_text_comment = {
            'post': 'Комментарий под постом',
            'text': 'Введите текст комментария',
        }
        comment = CommentModelTest.comment
        for field, expected_value in field_help_text_comment.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).help_text,
                    expected_value
                )
