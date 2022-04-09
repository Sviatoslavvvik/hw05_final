from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

import shutil
import tempfile

from ..models import Post, Group, Comment
from ..forms import PostForm, CommentForm

from http import HTTPStatus

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test-slug',
            description='Тестовое описание',
        )

        cls.form = PostForm()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(PostFormTests.user)
        cls.anonymous_client = Client()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_create(self):
        """Проверка создания поста авторизованным пользователм"""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый пост 1',
            'group': f'{PostFormTests.group.pk}',
            'image': uploaded
        }
        reverse_name = reverse('posts:post_create')
        response = PostFormTests.authorized_client.post(
            reverse_name,
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Код ответа не 200'
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostFormTests.user.username}
            )
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

        post = Post.objects.all().last()
        post_data = {
            'text': 'Тестовый пост 1',
            'author': PostFormTests.user,
            'group': PostFormTests.group,
            'image': 'posts/small.gif'
        }
        for field, value in post_data.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(post, field),
                    value
                )

    def test_post_edit(self):
        """Проверка редактирования поста автором"""

        upd_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='Test-slug-2',
            description='Тестовое описание 2',
        )

        post = Post.objects.create(
            author=PostFormTests.user,
            text='Тестовый пост',
            group=PostFormTests.group
        )
        reverse_name = reverse(
            'posts:post_edit',
            kwargs={'post_id': post.pk}
        )
        form_data = {
            'text': 'Тестовый пост 2',
            'group': f'{upd_group.pk}',
        }
        response = PostFormTests.authorized_client.post(
            reverse_name,
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Код ответа не 200'
        )
        post_data = {
            'text': 'Тестовый пост 2',
            'author': PostFormTests.user,
            'group': upd_group,
        }

        for field, value in post_data.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(Post.objects.get(pk=post.pk), field),
                    value
                )

        form_data_upd = {
            'text': 'Тестовый пост 3',
            'group': f'{upd_group.pk}',
        }
        response = PostFormTests.authorized_client.post(
            reverse_name,
            data=form_data_upd,
            follow=True,
        )
        post_data_upd = {
            'text': 'Тестовый пост 3',
            'author': PostFormTests.user,
            'group': upd_group,
        }
        for field, value in post_data_upd.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(Post.objects.get(pk=post.pk), field),
                    value
                )

    def test_post_edit_anonym(self):
        """Проверка редактирования поста анонимом"""
        upd_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='Test-slug-2',
            description='Тестовое описание 2',
        )
        post = Post.objects.create(
            author=PostFormTests.user,
            text='Тестовый пост',
            group=PostFormTests.group
        )

        form_data_anonym = {
            'text': 'Тестовый пост 2',
            'group': f'{upd_group.pk}',
        }
        reverse_name = reverse(
            'posts:post_edit',
            kwargs={'post_id': post.pk}
        )
        response = PostFormTests.anonymous_client.post(
            reverse_name,
            data=form_data_anonym,
            follow=True,
        )
        post_data = {
            'text': 'Тестовый пост',
            'author': PostFormTests.user,
            'group': PostFormTests.group
        }
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Код ответа не 200'
        )

        for field, value in post_data.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(Post.objects.get(pk=post.pk), field),
                    value
                )

    def test_post_create_anonymous(self):
        """Проверка создания поста анонимным пользователем"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 1',
            'group': f'{PostFormTests.group.pk}',
        }
        reverse_name = reverse('posts:post_create')
        PostFormTests.anonymous_client.post(
            reverse_name,
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), post_count)

    def test_post_edit_of_non_author(self):
        """Проверка редактирования поста
        зарегистрированным пользователем,
        но не автором
        """
        post = Post.objects.create(
            author=PostFormTests.user,
            text='Тестовый пост',
            group=PostFormTests.group
        )

        another_user = User.objects.create_user(username='New_user')
        another_authorized_client = Client()
        another_authorized_client.force_login(another_user)

        form_data_another = {
            'text': 'Тестовый пост 2',
            'group': '',
        }
        reverse_name = reverse(
            'posts:post_edit',
            kwargs={'post_id': post.pk}
        )
        response = another_authorized_client.post(
            reverse_name,
            data=form_data_another,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post.pk})
        )
        post_data = {
            'text': 'Тестовый пост',
            'author': PostFormTests.user,
            'group': PostFormTests.group,
        }
        for field, value in post_data.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(post, field),
                    value
                )

    def test_create_post_without_group(self):
        """Проверка создания поста без группы"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 1',
            'group': '',
        }
        reverse_name = reverse('posts:post_create')
        PostFormTests.authorized_client.post(
            reverse_name,
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

        post = Post.objects.all().last()
        post_data = {
            'text': 'Тестовый пост 1',
            'author': PostFormTests.user,
            'group': None,
        }
        for field, value in post_data.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(post, field),
                    value
                )


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.form = CommentForm()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(CommentFormTests.user)
        cls.anonymous_client = Client()
        # cls.anonymous_client = Client()

    def test_comment_create(self):
        """Проверка, что комментировать может только
        авторизованный пользователь"""

        some_post = Post.objects.create(
            author=CommentFormTests.user,
            text='Тестовый пост',
            group=None,
            image=None,
        )
        reverse_name = reverse(
            'posts:add_comment',
            kwargs={'post_id': some_post.pk}
        )
        form_data = {
            'text': 'Тестовый коммент',
        }
        response = CommentFormTests.authorized_client.post(
            reverse_name,
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Код ответа не 200'
        )
        comment = Comment.objects.filter(post=some_post.pk).last()
        self.assertEqual(
            comment.text,
            'Тестовый коммент'
        )

        comment_count = Comment.objects.all().count()

        response = CommentFormTests.anonymous_client.post(
            reverse_name,
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Код ответа не 200'
        )

        self.assertEqual(
            Comment.objects.all().count(),
            comment_count,
        )
