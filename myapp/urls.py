from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_index, name='blog_index'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<int:category_id>/', views.category_posts, name='category_posts'),
    path('category/create/', views.create_category, name='create_category'),
    path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('create/', views.create_post, name='create_post'),
    path('register/', views.register, name='register'),
    path('user/<str:username>/', views.user_posts, name='user_posts'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
]
