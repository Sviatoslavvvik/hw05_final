from django.test import TestCase, Client

from http import HTTPStatus


class AboutURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_acceses_for_all_user(self):
        """Проверяем доступность страниц по url"""
        urls_list = (
            '/about/author/',
            '/about/tech/',
        )
        for url in urls_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    'Код ответа не 200'
                )

    def test_urls_uses_correct_template(self):
        """Проверка вызова корректных шаблонов"""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
