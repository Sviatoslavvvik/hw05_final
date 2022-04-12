from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(PostURLTests.user)

    def test_acceses_for_urls_anonymous_user(self):
        """Проверяем доступность страниц по url анонимов"""
        urls_list = [
            '',
            f'/group/{PostURLTests.group.slug}/',
            f'/profile/{PostURLTests.user.username}/',
            f'/posts/{PostURLTests.post.pk}/',
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = PostURLTests.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    'Код ответа не 200'
                )

        urls_create_edit_anonym = [
            '/create/',
            f'/posts/{PostURLTests.post.pk}/edit/',
        ]
        for url in urls_create_edit_anonym:
            with self.subTest(url=url):
                response = PostURLTests.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.FOUND,
                    'Код ответа не 302'
                )
                self.assertRedirects(
                    response,
                    f'/auth/login/?next={url}',
                )

    def test_access_for_urls_defined_user(self):
        """Проверяем доступность страниц зарегистрированных пользователей"""
        urls_list = [
            '/create/',
            f'/posts/{PostURLTests.post.pk}/edit/',
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = PostURLTests.authorized_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    'Код ответа не 200'
                )

    def test_access_to_unexisting_page(self):
        """Проверяет доступ к несуществующей странице"""
        url = '/Unexisting_page/'
        response = PostURLTests.guest_client.get(url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            'Код ответа на 404'
        )

    def test_urls_uses_correct_template(self):
        """Проверяем что страницы использую правильные шаблоны"""
        templates_url_names = {
            '': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTests.user.username}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{PostURLTests.post.pk}/edit/': 'posts/create_post.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = PostURLTests.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_acces_to_edit_page_for_non_aythor(self):
        """Проверяем доступ к редактированию поста для неавтора"""

        another_user = User.objects.create_user(username='AnotherUser')
        another_authorized_client = Client()
        another_authorized_client.force_login(another_user)

        response = another_authorized_client.post(
            f'/posts/{PostURLTests.post.pk}/edit/'
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND,
            'Код ответа не 302'
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail', kwargs={'post_id': PostURLTests.post.pk},
            )
        )

    def test_access_to_comment_for_guest_user(self):
        """Провекра url комментирования для незарегистрированного
        пользователя"""
        url = f'/posts/{PostURLTests.post.pk}/comment/'
        response = PostURLTests.guest_client.get(url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND,
            'Код ответа не 302'
        )

    def test_access_to_comment_for_authprized_user(self):
        """Проверка url комментирования для зарегистрованного
        пользователя"""

        url = f'/posts/{PostURLTests.post.pk}/comment/'
        another_response = PostURLTests.authorized_client.get(url)

        self.assertEqual(
            another_response.status_code,
            HTTPStatus.FOUND,
            'Код ответа не 302'
        )
        self.assertRedirects(
            another_response,
            reverse(
                'posts:post_detail', kwargs={'post_id': PostURLTests.post.pk},
            )
        )
