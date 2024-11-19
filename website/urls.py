from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_record/', views.add_record, name='add_record'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('pending_records/', views.pending_records, name='pending_records'),  # Comment out until implemented
    path('approved-records/', views.approved_records, name='approved_records'),
    path('rejected_records/', views.rejected_records, name='rejected_records'),  # Commenting out until view is implemented
    path('my_records/', views.my_records, name='my_records'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('record/<int:pk>/edit/', views.edit_record, name='edit_record'),
    path('record/<int:pk>/delete/', views.delete_record, name='delete_record'),
    path('pending-records/', views.pending_records, name='pending_records'),
    path('rejected-records/', views.rejected_records, name='rejected_records'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:pk>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('record/<int:pk>/approve/', views.record_approval, name='record_approval'),
    path('record/<int:pk>/', views.record_detail, name='record_detail'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('api/notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]