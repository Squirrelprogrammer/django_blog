from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from blog.models import Post
from blog.forms import PostForm
from rest_framework.test import APIClient
from rest_framework import status

from blog.serializers import PostsSerializer

User = get_user_model()


class PostModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_post(self):
        post = Post.objects.create(
            author=self.user,
            title='Test title',
            text='Test content',
            created_date=timezone.now()
        )
        self.assertEqual(str(post), 'Test title')
        self.assertEqual(post.title, 'Test title')
        self.assertEqual(post.text, 'Test content')

    def test_publish_post(self):
        post = Post.objects.create(
            author=self.user,
            title='Test title',
            text='Test content',
            created_date=timezone.now()
        )
        self.assertIsNone(post.published_date)
        post.publish()
        self.assertIsNotNone(post.published_date)
        self.assertAlmostEqual(post.published_date, timezone.now(), delta=timezone.timedelta(seconds=1))


class PostFormTest(TestCase):

    def setUp(self):
        self.data = {'title': 'Form test title', 'text': 'Form test content'}
        self.invalid_data_missing_title = {'text': 'Form test content'}
        self.invalid_data_missing_text = {'title': 'Form test title'}

    def test_valid_form(self):
        form = PostForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_title(self):
        form = PostForm(data=self.invalid_data_missing_title)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_invalid_form_missing_text(self):
        form = PostForm(data=self.invalid_data_missing_text)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)


class SerializerTest(TestCase):

    def setUp(self):
        self.data = {'title': 'Serializer test title', 'text': 'Serializer test content'}
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(
            author=self.user,
            title='Serializer test title',
            text='Serializer test content',
            created_date=timezone.now()
        )

    def test_serializer_fields(self):
        serializer = PostsSerializer(instance=self.post)
        data = serializer.data
        self.assertIn('id', data)
        self.assertEqual(data['title'], self.post.title)
        self.assertEqual(data['text'], self.post.text)
        self.assertNotIn('author', data)
        self.assertNotIn('created_date', data)
        self.assertNotIn('published_date', data)

    def test_create_post(self):
        request = type('Request', (), {'user': self.user})()
        serializer = PostsSerializer(data=self.data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        post = serializer.save()
        self.assertEqual(post.title, 'Serializer test title')
        self.assertEqual(post.text, 'Serializer test content')
        self.assertEqual(post.author, self.user)


class ViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user=self.user)
        self.data = {'title': 'ViewSet test title', 'text': 'ViewSet test content'}
        self.post = Post.objects.create(
            author=self.user,
            title='ViewSet test title',
            text='ViewSet test content',
            created_date=timezone.now()
        )

    def test_posts(self):
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data[0])
        self.assertIn('title', response.data[0])
        self.assertIn('text', response.data[0])

    def test_create_post(self):
        data = self.data
        response = self.client.post('/api/posts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'ViewSet test title')
        self.assertEqual(response.data['text'], 'ViewSet test content')

    def test_update_post(self):
        url = f'/api/posts/{self.post.pk}/'
        data = self.data
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'ViewSet test title')
        self.assertEqual(self.post.text, 'ViewSet test content')


class ViewFunctionsTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(self.user)
        self.data = {'title': 'ViewFunctions test title', 'text': 'ViewFunctions test content'}
        self.new_data = {'title': 'New test title', 'text': 'New test content'}
        self.post = Post.objects.create(
            author=self.user,
            title='ViewFunctions test title',
            text='ViewFunctions test content',
            created_date=timezone.now()
        )
        self.post_detail_url = reverse('post_detail', args=[self.post.pk])

    def test_post_detail(self):
        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.text)

    def test_post_new_get(self):
        url = reverse('post_new')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form')
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="text"')

    def test_post_new_post(self):
        url = reverse('post_new')
        data = self.new_data
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='New test title').exists())
        post = Post.objects.get(title='New test title')
        self.assertEqual(post.author, self.user)

    def test_post_edit_get(self):
        url = reverse('post_edit', args=[self.post.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.text)

    def test_post_edit_post(self):
        url = reverse('post_edit', args=[self.post.pk])
        data = self.data
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'ViewFunctions test title')
        self.assertEqual(self.post.text, 'ViewFunctions test content')
