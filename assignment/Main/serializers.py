from rest_framework import serializers
from .models import User, Post, Like
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core import exceptions as django_exceptions
from django.contrib.auth import password_validation




class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id','username', 'email', 'password','first_name' ,'confirm_password']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')



        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError("Password and Confirm Password do not match.")
        

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        confirm_password = validated_data.pop('confirm_password')

        if password and confirm_password and password == confirm_password:
            user = User.objects.create_user(password=password, **validated_data)
            return user

class PostSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'content', 'creation_date', 'is_public', 'owner','likes_count']

    def get_likes_count(self, post):
        return post.like_set.count()


class UpdatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'description', 'content', 'is_public']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'like_date']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        extra_kwargs = {
            'username': {'required': False},
            'password': {'required': False},
            'confirm_password': {'required': False},
        }