"""
Test for comments API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Comment,
    Blog
)


COMMENT_URL = reverse('blog:comment-list')

def detail_url(comment_id):
    """Create and return a blog detail URL."""
    return reverse('blog:comment-detail', args=[comment_id])

def blog_comments_url(blog_id):
    return reverse('blog:comment-list', args=blog_id)

def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)

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


class AuthentiatedCommentAPITests(TestCase):
    """Authenticated tests for Comments API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_creating_comment(self):
        """Test creating a new comment."""
        blog = create_blog(
            author=self.user,
            title='This is test blog title',
            excerpt='This is test Excerpt.',
            content='This is test content',
        )
        
        payload = {
            'comment_text': 'This is a test comment.',
            'blog': blog.id,
            'author': self.user.id,
            'likes_count': 3
        }

        res = self.client.post(COMMENT_URL, payload)
        comment = Comment.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    
        self.assertEqual(comment.comment_text, payload['comment_text'])

    def test_deleting_comment(self):
        """Test deleting a comment."""
        blog = create_blog(
            author=self.user,
            title='This is test blog title',
            excerpt='This is test Excerpt.',
            content='This is test content',
        )
        
        comment = Comment.objects.create(
            comment_text='This is a test comment.',
            blog=blog,
            author=self.user,
            likes_count=3
        )

        url = detail_url(comment.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_updating_comment_text(self):
        """Test updating comment text."""
        blog = create_blog(
            author=self.user,
            title='This is test blog title',
            excerpt='This is test Excerpt.',
            content='This is test content',
        )
        
        comment = Comment.objects.create(
            comment_text='This is a test comment.',
            blog=blog,
            author=self.user,
            likes_count=3
        )

        url = detail_url(comment.id)
        payload = {'comment_text': 'This is new comment text'}
        res = self.client.patch(url, payload)
        comment.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(comment.comment_text, payload['comment_text'])

    def test_updating_comment_likes_count(self):
        """Test updating comment likes count."""
        blog = create_blog(
            author=self.user,
            title='This is test blog title',
            excerpt='This is test Excerpt.',
            content='This is test content',
        )
        
        comment = Comment.objects.create(
            comment_text='This is a test comment.',
            blog=blog,
            author=self.user,
            likes_count=3
        )

        url = detail_url(comment.id)
        payload = {'likes_count': '30'}
        res = self.client.patch(url, payload)
        comment.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(comment.likes_count, int(payload['likes_count']))

    def test_changing_comment_blog_result_raises_error(self):
        """Test updating comment's blog should result in error"""
        blog1 = create_blog(
            author=self.user,
            title='This is test blog title',
            excerpt='This is test Excerpt.',
            content='This is test content',
        )

        blog2 = create_blog(
            author=self.user,
            title='This is another test blog title',
            excerpt='This is another test Excerpt.',
            content='This is another test content',
        )
        
        comment = Comment.objects.create(
            comment_text='This is a test comment.',
            blog=blog1,
            author=self.user,
            likes_count=3
        )

        url = detail_url(comment.id)
        self.client.patch(url, {'blog': blog2.id})
        comment.refresh_from_db()

        self.assertEqual(comment.blog, blog1)
        


    def test_changing_comment_author(self):
        """Test updating comment's author should raise error."""
        blog = create_blog(
            author=self.user,
            title='This is test blog title',
            excerpt='This is test Excerpt.',
            content='This is test content',
        )
        
        user2 = create_user(email='user2@example.com', password='testpass123')

        comment = Comment.objects.create(
            comment_text='This is a test comment.',
            blog=blog,
            author=self.user,
            likes_count=3
        )

        url = detail_url(comment.id)
        self.client.patch(url, {'author': user2.id})

        comment.refresh_from_db()
        self.assertEqual(comment.author, self.user)