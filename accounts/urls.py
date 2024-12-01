from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_2fa

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('2fa/setup/', views_2fa.setup_2fa, name='setup_2fa'),
    path('2fa/verify/', views_2fa.verify_2fa, name='verify_2fa'),
    path('2fa/disable/', views_2fa.disable_2fa, name='disable_2fa'),
    path('verify-2fa-login/', views.verify_2fa_login, name='verify_2fa_login'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='create_user'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='edit_user'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='delete_user'),
    path('users/<int:pk>/change-password/', views.UserPasswordChangeView.as_view(), name='change_password'),
]
