import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


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

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test-slug',
            description='Тестовое описание',
        )
        cls.form = PostForm()

    def setUp(self):
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.anonymous_client = Client()

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
            'group': PostFormTests.group.pk,
            'image': uploaded
        }
        reverse_name = reverse('posts:post_create')
        response = self.authorized_client.post(
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
                kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

        post = Post.objects.all().last()
        post_data = {
            'text': 'Тестовый пост 1',
            'author': self.user,
            'group': PostFormTests.group,
            'image': 'posts/small.gif'
        }
        for field, value in post_data.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(post, field),
                    value
                )

    def test_post_edit_group_not_changed(self):
        """Проверка редактирования поста автором
        БЕЗ изменения группы"""

        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=PostFormTests.group
        )
        reverse_name = reverse(
            'posts:post_edit',
            kwargs={'post_id': post.pk}
        )

        form_data = {
            'text': 'Изменили пост ',
            'group': PostFormTests.group.pk,
        }
        response = self.authorized_client.post(
            reverse_name,
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Код ответа не 200'
        )

        post_data_upd = {
            'text': 'Изменили пост',
            'author': self.user,
            'group': PostFormTests.group,

        }
        post_for_checking = Post.objects.get(id=post.pk)

        for field, value in post_data_upd.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(post_for_checking, field),
                    value
                )

    def test_post_edit_group_change(self):
        """Проверка редактирования поста автором
        c изменением группы"""

        upd_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='Test-slug-2',
            description='Тестовое описание 2',
        )

        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=PostFormTests.group
        )
        reverse_name = reverse(
            'posts:post_edit',
            kwargs={'post_id': post.pk}
        )
        form_data = {
            'text': 'Тестовый пост 2',
            'group': upd_group.pk,
        }
        response = self.authorized_client.post(
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
            'author': self.user,
            'group': upd_group,
            'text': 'Тестовый пост 2'
        }

        for field, value in post_data.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(Post.objects.get(pk=post.pk), field),
                    value
                )

    def test_post_edit_image_change(self):
        """Проверка редактирования поста автором
        c изменением картинки"""
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
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=PostFormTests.group,
            image=uploaded,
        )
        small_gif_change = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_upd = SimpleUploadedFile(
            name='small_change.gif',
            content=small_gif_change,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Тестовый пост 2',
            'group': PostFormTests.group.pk,
            'image': uploaded_upd
        }
        reverse_name = reverse(
            'posts:post_edit',
            kwargs={'post_id': post.pk}
        )
        response = self.authorized_client.post(
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
            'author': self.user,
            'group': PostFormTests.group,
            'text': 'Тестовый пост 2',
            'image': 'posts/small_change.gif'
        }
        for field, value in post_data.items():
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
            author=self.user,
            text='Тестовый пост',
            group=PostFormTests.group
        )

        form_data_anonym = {
            'text': 'Тестовый пост 2',
            'group': upd_group.pk,
        }
        reverse_name = reverse(
            'posts:post_edit',
            kwargs={'post_id': post.pk}
        )
        response = self.anonymous_client.post(
            reverse_name,
            data=form_data_anonym,
            follow=True,
        )
        post_data = {
            'text': 'Тестовый пост',
            'author': self.user,
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
            'group': PostFormTests.group.pk,
        }
        reverse_name = reverse('posts:post_create')
        self.anonymous_client.post(
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
            author=self.user,
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
            'author': self.user,
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
        self.authorized_client.post(
            reverse_name,
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

        post = Post.objects.all().last()
        post_data = {
            'text': 'Тестовый пост 1',
            'author': self.user,
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
        cls.some_post = Post.objects.create(
            author=CommentFormTests.user,
            text='Тестовый пост',
        )

    def test_comment_create(self):
        """Проверка, что комментировать может только
        авторизованный пользователь"""

        reverse_name = reverse(
            'posts:add_comment',
            kwargs={'post_id': CommentFormTests.some_post.pk}
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
        comment = Comment.objects.filter(
            post=CommentFormTests.some_post.pk
        ).last()
        self.assertEqual(
            comment.text,
            'Тестовый коммент'
        )

    def test_anonym_not_access_to_comment(self):
        comment_count = Comment.objects.all().count()
        reverse_name = reverse(
            'posts:add_comment',
            kwargs={'post_id': CommentFormTests.some_post.pk}
        )
        form_data = {
            'text': 'Тестовый коммент',
        }

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
