"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTest(TestCase):
    """Test models."""
    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new user."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'testpass123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating a user without email create a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testpass123')

    def test_creating_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_blog_successful(self):
        """Test creating blog with valid information results in successful blog creation."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        blog = models.Blog.objects.create(
            author=user,
            title="Sample Blog Title",
            excerpt="This is a test blog excerpt.",
            content="Some test content regarding the test blog.",
        )

        self.assertEqual(str(blog), blog.title)

    def test_creating_comment_without_text_raises_error(self):
        """Test submitting a comment without any body raises a error."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        blog = models.Blog.objects.create(
            author=user,
            title="Sample Blog Title",
            excerpt="This is a test blog excerpt.",
            content="Some test content regarding the test blog.",
        )

        comment = models.Comment.objects.create(
            author = user,
            comment_text = "This is test comment",
            blog = blog,
            likes_count = 3
        )

        self.assertEqual(str(comment), comment.comment_text)
