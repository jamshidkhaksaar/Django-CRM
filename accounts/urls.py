from django.urls import path
from . import views
from .views import CustomPasswordChangeView

urlpatterns = [
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.CreateUserView.as_view(), name='create_user'),
    path('users/<int:pk>/edit/', views.EditUserView.as_view(), name='edit_user'),
    path('users/<int:pk>/delete/', views.DeleteUserView.as_view(), name='delete_user'),
    path('users/<int:pk>/change-password/', CustomPasswordChangeView.as_view(), name='change_password'),
]
