from django.urls import path
from . import views
from .views import (
    UserListView, CreateUserView, EditUserView, 
    DeleteUserView, CustomPasswordChangeView, CustomLoginView
)

urlpatterns = [
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', CreateUserView.as_view(), name='create_user'),
    path('users/<int:pk>/edit/', EditUserView.as_view(), name='edit_user'),
    path('users/<int:pk>/delete/', DeleteUserView.as_view(), name='delete_user'),
    path('users/<int:pk>/change-password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('login/', CustomLoginView.as_view(), name='login'),
]
