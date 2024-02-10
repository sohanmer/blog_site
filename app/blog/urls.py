"""
Url mappings for the blog API
"""
from django.urls import (
    path, 
    include
)

from rest_framework.routers import DefaultRouter

from blog import views

router = DefaultRouter()
router.register('blogs', views.BlogViewSet, basename='blog')
router.register('tags', views.TagViewSet, basename='tag')
router.register('comments', views.CommentViewSet, basename='comment')

app_name = 'blog'

urlpatterns = [
    path('', include(router.urls)),
]
