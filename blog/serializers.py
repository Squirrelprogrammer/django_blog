from typing import Mapping
from rest_framework import serializers
from django.contrib.auth.models import User

from blog.models import Post


class PostsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ['id', 'title', 'text']
        read_only_fields = ['author', 'created_date', 'published_date']

    def create(self, validated_data: Mapping[str]) -> Post:
        user: User = self.context['request'].user
        post: Post = Post.objects.create(author=user, **validated_data)
        return post
