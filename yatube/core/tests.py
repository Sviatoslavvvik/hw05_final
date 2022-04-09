from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class UnexistingPageTests(TestCase):

    def test_access_to_unexisting_page(self):
        """Проверяем что страница 404 отдает кастомный шаблон."""
        url = '/Unexisting_page/'
        template = 'core/404.html'
        user = User.objects.create_user(username='HasNoName')
        authorized_client = Client()
        authorized_client.force_login(user)
        response = authorized_client.get(url)
        self.assertTemplateUsed(response, template)
