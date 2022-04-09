from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from http import HTTPStatus

User = get_user_model()


class UserURLTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_acceses_for_all_user(self):
        """Проверяем доступность страниц по url"""
        urls_list = [
            '/auth/signup/',
            '/auth/logout/',
            '/auth/login/',
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.reason_phrase, HTTPStatus.OK.phrase)

    def test_acceses_for_defined_user(self):
        """Проверяем доступность страниц по url"""
        urls_list = [
            '/auth/password_change/done/',
            '/auth/password_change/'
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.reason_phrase,
                                 HTTPStatus.FOUND.phrase)

    def test_urls_uses_correct_template_anonym(self):
        """Проверка вызова корректных шаблонов нузалог пользователей"""
        templates_url_names = {
            'users/logged_out.html': '/auth/logout/',
            'users/login.html': '/auth/login/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_defined_user(self):
        """Проверка вызова корректных шаблонов залогиненого пользователя"""
        templates_url_names = {

            'users/password_change_done.html': '/auth/password_change/done/',
            'users/password_change_form.html': '/auth/password_change/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
