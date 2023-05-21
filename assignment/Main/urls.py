from django.urls import path, include
from .views import *

urlpatterns = [
    path('api/register/', create_user, name='create_user'),
    path('api/users/<int:user_id>/', get_user, name='get_user'),
    path('api/users/update/<int:user_id>/', update_user, name='update_user'),
    path('api/get_all_users/', get_all_users, name='get_all_users'),
    path('api/login/', login_view, name='login'),

    path('api/create_post/', create_post, name='create_post'),
    path('api/get_posts/<int:post_id>/', get_post, name='get_post'),
    path('api/get_all_posts/', get_all_posts, name='get_all_post'),
    path('api/update_posts/<int:post_id>/', update_post, name='update_post'),
    path('api/delete_posts/<int:post_id>/', delete_post, name='delete_post'),
    
    # Like URL
    path('api/posts/<int:post_id>/like/', like_post, name='like_post'),
]