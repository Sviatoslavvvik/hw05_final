import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..models import Group, Post, Comment, Follow
from ..forms import PostForm, CommentForm

User = get_user_model()

TEST_POST_AMOUNT = 14
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PaginatorViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test-slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='Test-slug-2',
            description='Тестовое описание 2',
        )
        post_list = (Post(
            author=cls.user,
            text=f'Тестовый пост {i}',
            group=cls.group
        ) for i in range(TEST_POST_AMOUNT))

        Post.objects.bulk_create(post_list)

        cls.authorized_client = Client()
        cls.authorized_client.force_login(PaginatorViewTests.user)

    def test_first_page_contains_ten_records(self):
        """Проверка что первая страница паджинатора имеет 10 записей"""
        reverse_name_list = (
            reverse('posts:all posts'),
            reverse(
                'posts:sorted_posts',
                kwargs={'slug': PaginatorViewTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewTests.user.username}
            )
        )
        for reverse_name in reverse_name_list:
            with self.subTest(reverse_name=reverse_name):
                response = PaginatorViewTests.authorized_client.get(
                    reverse_name
                )
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.SORTED_VALUES_AMOUNT
                )

    def test_second_page_contains_fourth_records(self):
        """Проверка что вторая страница паджинатора имеет 4 записи"""
        reverse_name_list = (
            reverse('posts:all posts'),
            reverse(
                'posts:sorted_posts',
                kwargs={'slug': PaginatorViewTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewTests.user.username}
            )
        )
        for reverse_name in reverse_name_list:
            with self.subTest(reverse_name=reverse_name):
                response = PaginatorViewTests.authorized_client.get(
                    reverse_name + '?page=2'
                )
                self.assertEqual(
                    len(response.context['page_obj']),
                    TEST_POST_AMOUNT - settings.SORTED_VALUES_AMOUNT
                )

    def test_pages_with_paginator_have_correct_context(self):
        """Проверка что  страницы с паджинатором имеют правильный контекст"""
        reverse_name_list = (
            reverse('posts:all posts'),
            reverse(
                'posts:sorted_posts',
                kwargs={'slug': PaginatorViewTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewTests.user.username}
            )
        )
        for reverse_name in reverse_name_list:
            with self.subTest(reverse_name=reverse_name):
                response = PaginatorViewTests.authorized_client.get(
                    reverse_name
                )
                self.assertIn(
                    'Тестовый пост',
                    response.context.get('page_obj').object_list[0].text,
                )
                self.assertEqual(
                    response.context.get('page_obj').object_list[0].author,
                    PaginatorViewTests.user,
                )
                self.assertEqual(
                    response.context.get('page_obj').object_list[0].group,
                    PaginatorViewTests.group,
                )


class PostViewTests(TestCase):
    @classmethod
    def setUp(self):

        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test-slug',
            description='Тестовое описание',
        )
        self.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='Test-slug-2',
            description='Тестовое описание 2',
        )
        post_list = (Post(
            author=self.user,
            text=f'Тестовый пост {i}',
            group=self.group,
        ) for i in range(TEST_POST_AMOUNT))

        Post.objects.bulk_create(post_list)
        self.some_post = Post.objects.all().last()

        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTests.user)

    def test_pages_uses_correct_template(self):
        """Проверка вызова корректных шаблонов"""

        templates_pages_names = {
            reverse('posts:all posts'): 'posts/index.html',
            reverse(
                'posts:sorted_posts',
                kwargs={'slug': PostViewTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.some_post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.some_post.pk}
            ): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = PostViewTests.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_contains_list_of_posts(self):
        """Проверка что страница index содержит список постов"""
        response = PostViewTests.authorized_client.get(
            reverse('posts:all posts')
        )

        for post_example in response.context.get('page_obj').object_list:
            with self.subTest():
                self.assertIsInstance(post_example, Post)

    def test_group_contains_list_of_posts(self):
        """Проверка что group_list содержит посты, отфильтрованные по группе"""
        response = PostViewTests.authorized_client.get(
            reverse(
                'posts:sorted_posts',
                kwargs={'slug': PostViewTests.group.slug},
            ))
        for post_example in response.context.get('page_obj').object_list:
            with self.subTest():
                self.assertIsInstance(post_example, Post)
                self.assertEqual(post_example.group, PostViewTests.group)

    def test_profile_contains_list_of_posts(self):
        """Проверка что profile содержит посты, отфильтрованные по автору"""
        response = PostViewTests.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.user.username}
            ))
        for post_example in response.context.get('page_obj').object_list:
            with self.subTest():
                self.assertIsInstance(post_example, Post)
                self.assertEqual(post_example.author, PostViewTests.user)

    def test_post_detail_contains_correct_context(self):
        """Проверка что post_detail содержит правильный контекст"""
        comment = Comment.objects.create(
            text='Тестовый коммент',
            post=PostViewTests.some_post,
            author=PostViewTests.user,
        )
        response = PostViewTests.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewTests.some_post.pk}
            ))
        comments_count = Comment.objects.filter(
            post=PostViewTests.some_post
        ).count()
        response_form = response.context.get('form')
        self.assertIsInstance(response_form, CommentForm)
        self.assertEqual(response.context['post'], PostViewTests.some_post)
        self.assertEqual(response.context['comments'].count(), comments_count)
        self.assertEqual(response.context['comments'].last(), comment)

    def test_post_edit_contains_post_edit_form(self):
        """Проверка, что post_edit содержит форму PostForm"""
        response = PostViewTests.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewTests.some_post.pk}
            ))
        response_form = response.context.get('form')
        self.assertIsInstance(response_form, PostForm)

    def test_post_create_contains_post_edit_form(self):
        """Проверка, что post_create содержит форму PostForm"""
        response = PostViewTests.authorized_client.get(
            reverse('posts:post_create'))
        response_form = response.context.get('form')
        self.assertIsInstance(response_form, PostForm)

    def test_post_create(self):
        """Проверки:
        1. Вновь созданный пост отображается на главной странице;
        2. Вновь созданный пост отображается на странице групп;
        3.Вновь созданный пост отображается на странице автора;
        4.Вновь созданный пост не отображается на странице
        неправильной групп"""
        new_post = Post.objects.create(
            author=self.user,
            text='Новый Тестовый пост',
            group=self.group
        )
        response_index = self.authorized_client.get(
            reverse('posts:all posts')
        )
        self.assertEqual(
            new_post,
            response_index.context.get('page_obj').object_list[0]
        )
        response_group = PostViewTests.authorized_client.get(
            reverse(
                'posts:sorted_posts',
                kwargs={'slug': PostViewTests.group.slug}
            )
        )
        self.assertIn(
            new_post,
            response_group.context.get('page_obj').object_list
        )
        response_profile = PostViewTests.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.user.username}
            )
        )
        self.assertIn(
            new_post,
            response_profile.context.get('page_obj').object_list
        )
        response_group_2 = PostViewTests.authorized_client.get(
            reverse(
                'posts:sorted_posts',
                kwargs={'slug': PostViewTests.group_2.slug}
            )
        )
        self.assertNotIn(
            new_post,
            response_group_2.context.get('page_obj').object_list
        )

    def test_index_page_cach(self):
        """Проверяем кэширование главной страницы"""
        response = self.authorized_client.get(
            reverse('posts:all posts')
        )

        cached = response.content
        self.some_post.delete()

        upd_response = self.authorized_client.get(
            reverse('posts:all posts')
        )
        cached_again = upd_response.content
        self.assertEqual(cached, cached_again, 'Страница не кэшируется')

    def test_cache_removed_after_delete(self):
        """Проверка, что пост пропадает после
        принудительной очистки кэша"""
        response = self.authorized_client.get(
            reverse('posts:all posts')
        )
        content_before_delete = response.context.get('page_obj').object_list

        self.some_post.delete()
        cache.delete('index_page')

        response_after_cache_delete = self.authorized_client.get(
            reverse('posts:all posts')
        )

        content_after_delete = response_after_cache_delete.context.get(
            'page_obj'
        ).object_list

        self.assertNotEqual(
            content_before_delete,
            content_after_delete,
        )

    def test_following(self):
        """Проверка подписки авторизованного пользователя"""
        another_user = User.objects.create_user(username='new_user')
        another_authorized_client = Client()
        another_authorized_client.force_login(another_user)

        another_authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user.username},
            ))

        subscription = Follow.objects.last()

        subs_data = {
            'author': self.user,
            'user': another_user,
        }
        for field, value in subs_data.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(subscription, field),
                    value
                )

    def test_unfollowing(self):
        """Проверка отписки авторизованного пользователя"""
        another_user = User.objects.create_user(username='new_user')
        another_authorized_client = Client()
        another_authorized_client.force_login(another_user)

        another_authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user.username},
            ))
        another_authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user.username},
            ))

        self.assertIsNone(Follow.objects.last())

    def test_new_post_appering_follower(self):
        """Проверка что новая запись пользователя
        появляется у подписчиков и не появляется
        у не подписанных пользователей"""
        follower_user = User.objects.create_user(username='follower')
        follower_authorized_client = Client()
        follower_authorized_client.force_login(follower_user)

        Follow.objects.create(
            author=self.user,
            user=follower_user
        )

        response = follower_authorized_client.get(
            reverse('posts:follow_index'))

        self.assertIn(
            'Тестовый пост',
            response.context.get('page_obj').object_list[0].text,
        )
        self.assertEqual(
            response.context.get('page_obj').object_list[0].author,
            self.user,
        )
        self.assertEqual(
            response.context.get('page_obj').object_list[0].group,
            self.group,
        )

        not_follower_user = User.objects.create_user(username='nonfollower')
        not_follower_authorized_client = Client()
        not_follower_authorized_client.force_login(not_follower_user)

        response = not_follower_authorized_client.get(
            reverse('posts:follow_index'))

        self.assertNotIn(
            Post.objects.all(),
            response.context.get('page_obj').object_list
        )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostWithImageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded,
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(PostWithImageTests.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_image_transmitting_in_context(self):
        """Проверка что картинка передаётся в контексте"""
        reverse_name_list = (
            reverse('posts:all posts'),
            reverse(
                'posts:sorted_posts',
                kwargs={'slug': PostWithImageTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostWithImageTests.user.username}
            ),
        )
        for reverse_name in reverse_name_list:
            with self.subTest(reverse_name=reverse_name):
                response = PostWithImageTests.authorized_client.get(
                    reverse_name
                )
                self.assertEqual(
                    response.context.get('page_obj').object_list[0].image,
                    PostWithImageTests.post.image,
                )
        reverse_name = reverse(
            'posts:post_detail',
            kwargs={'post_id': PostWithImageTests.post.pk}
        )
        self.assertEqual(
            response.context['post'].image,
            PostWithImageTests.post.image
        )
