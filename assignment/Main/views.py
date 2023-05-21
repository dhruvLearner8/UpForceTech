from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User, Post, Like
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, get_user_model
from django.http import JsonResponse
from .serializers import UserSerializer, PostSerializer, LikeSerializer, UserUpdateSerializer,UpdatePostSerializer
# Create your views here.
from django.contrib.auth.decorators import login_required

from rest_framework_simplejwt.tokens import RefreshToken

UserModel = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        password = serializer.validated_data['password']
        confirm_password = serializer.validated_data['confirm_password']
        if password == confirm_password:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            error_message = {'error': 'Password and Confirm Password do not match.'}
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        token = get_tokens_for_user(user)
        return Response({'token':token,'msg':'Login Success'},status=status.HTTP_200_OK)
    else:
        return JsonResponse({'message': 'Invalid credentials'}, status=401)

@api_view(['GET'])
def get_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
def update_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserUpdateSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    data = request.data
    data['owner'] = request.user.id
    serializer = PostSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_posts(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the post is public or the current user is the owner
    if not post.is_public and post.owner != request.user:
        return Response({"detail": "You do not have permission to access this post."}, status=status.HTTP_403_FORBIDDEN)

    serializer = PostSerializer(post)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdatePostSerializer(post, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    post.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

    user = request.user

    # Check if the user has already liked the post
    if Like.objects.filter(post=post, user=user).exists():
        return Response({"detail": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)

    # Create a new Like object
    like = Like(post=post, user=user)
    like.save()

    return Response({"detail": "Post liked successfully."}, status=status.HTTP_201_CREATED)