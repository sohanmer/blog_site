"""
Views for the blog APIs.
"""
from django.shortcuts import render
from rest_framework import generics, authentication, permissions
from rest_framework import (
    viewsets,
    mixins,
    status,
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import AuthenticatedOrListOnly, IsOwnerOrReadOnly
from rest_framework.views import APIView

from core.models import (
    Blog,
    Tag,
)
from blog import serializers


class BlogViewSet(
        viewsets.ModelViewSet,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin
    ):
    """Views to provide api for blog API"""
    serializer_class = serializers.BlogSerializer
    queryset = Blog.objects.all().order_by('-id').distinct()
    authentication_classes = [TokenAuthentication]
    permission_classes = [AuthenticatedOrListOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        """Create a new blog."""
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    """Manage tags in the database."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all().order_by('-name').distinct()
