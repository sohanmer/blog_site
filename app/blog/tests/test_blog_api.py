"""
Tests for blog APIs.
"""
from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Blog,
    Tag,
    Comment,
)

from blog.serializers import (
    BlogSerializer,
    )


BLOG_URL = reverse('blog:blog-list')

def blog_comments_url(blog_id):
    return reverse('blog:comment-list', args=blog_id)

def detail_url(blog_id):
    """Create and return a blog detail URL."""
    return reverse('blog:blog-detail', args=[blog_id])


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

def create_blog(author, **params):
    """Create and return sample blog."""
    defaults = {
        'title': 'Sample blog title',
        'excerpt': 'Sample blog excerpt.',
        'content': 'This content is a Sample blog content.'
    }
    defaults.update(**params)

    blog = Blog.objects.create(author=author, **defaults)
    return blog


class PublicBlogAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')

    def test_unauthenticated_request_can_get_blog_list(self):
        """Test unauthenticated API requests can get the blog list."""
        create_blog(author=self.user)
        create_blog(author=self.user)

        res = self.client.get(BLOG_URL)

        blogs = Blog.objects.all().order_by('-id')
        serializer = BlogSerializer(blogs, many=True)
        self.assertEqual(res.data, serializer.data)


class PrivateBlogAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_create_blog(self):
        """Test creating a blog."""
        payload = {
        'title': 'Sample blog title',
        'excerpt': 'Sample blog excerpt.',
        'content': 'This content is a Sample blog content.'
        }
        res = self.client.post(BLOG_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        blog = Blog.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(blog, k), v)
        self.assertEqual(blog.author, self.user)

    def test_partial_update_blog(self):
        """Test updating a blog."""
        original_title = 'Original title'
        original_content = 'This is test Content.'
        blog = create_blog(
            author=self.user,
            title=original_title,
            excerpt='This is test Excerpt.',
            content=original_content,
        )

        payload = {'excerpt': 'New blog excerpt'}
        url = detail_url(blog.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        blog.refresh_from_db()
        self.assertEqual(blog.title, original_title)
        self.assertEqual(blog.excerpt, payload['excerpt'])
        self.assertEqual(blog.content, original_content)
        self.assertEqual(blog.author, self.user)

    def test_full_update_blog(self):
        blog = create_blog(
            author=self.user,
            title='This is test blog title',
            excerpt='This is test Excerpt.',
            content='This is test content',
        )

        payload = {
            'title': 'New blog title',
            'excerpt': 'New blog excerpt',
            'content': 'New blog content'
        }

        url = detail_url(blog.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        blog.refresh_from_db()
        self.assertEqual(blog.title, payload['title'])
        self.assertEqual(blog.excerpt, payload['excerpt'])
        self.assertEqual(blog.content, payload['content'])
        self.assertEqual(blog.author, self.user)

    def test_update_author_return_error(self):
        """Test updating author of a blog return error."""
        author = create_user(email='test@example.com', password='testpass123')
        blog = create_blog(author=self.user)

        payload = {'author': author.id}
        url = detail_url(blog.id)
        self.client.patch(url, payload)

        blog.refresh_from_db()
        self.assertEqual(blog.author, self.user)

    def test_delete_blog(self):
        """Test deleting blog."""
        blog = create_blog(author=self.user)

        url = detail_url(blog.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Blog.objects.filter(id=blog.id).exists())

    def test_delete_other_users_blog_error(self):
        """Test deleting other user's blog results in error."""
        new_user = create_user(email='user2@example.com', password='testpass123')
        blog = create_blog(author=new_user)

        url = detail_url(blog.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Blog.objects.filter(id=blog.id).exists())

    def test_retrieving_blog_comments(self):
        """Test retrieving all blog comments."""
        user2 = create_user(email='user2@example.com', password='testpass123')
        blog = create_blog(author=self.user)
        comment1 = Comment.objects.create(
            comment_text = "This is a test comment.",
            author = self.user,
            blog = blog,
            likes_count = 5
        )
        comment2 = Comment.objects.create(
            comment_text = "This is a another comment.",
            author = user2,
            blog = blog,
            likes_count = 2
        )

        url = detail_url(blog_id=blog.id)
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['comments']), 2)
        self.assertEqual(Comment.objects.get(id=res.data['comments'][0]['author']).author, self.user)
        self.assertEqual(Comment.objects.get(id=res.data['comments'][1]['author']).author, user2)
