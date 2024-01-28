"""
Serializer for blog APIs.
"""
from rest_framework import serializers

from core.models import (
    Blog,
    Tag,
)


class TagSerializer(serializers.ModelSerializer):
    """Serializers for tags."""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class BlogSerializer(serializers.ModelSerializer):
    """Serializer for Blog."""
    tags = TagSerializer(many=True, required=False)
    class Meta:
        model = Blog
        fields = [
            'id',
            'title',
            'excerpt',
            'content',
            'tags'
        ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, blog):
        """Handle  getting or creating tags as needed."""
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                **tag,
            )
            blog.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a Blog."""
        tags = validated_data.pop('tags', [])
        blog = Blog.objects.create(**validated_data)
        self._get_or_create_tags(tags, blog)

        return blog