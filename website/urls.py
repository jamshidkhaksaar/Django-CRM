from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_record/', views.add_record, name='add_record'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('pending_records/', views.pending_records, name='pending_records'),
    path('approved_records/', views.approved_records, name='approved_records'),
    path('rejected_records/', views.rejected_records, name='rejected_records'),
    path('my_records/', views.my_records, name='my_records'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('record/<int:pk>/edit/', views.edit_record, name='edit_record'),
    path('record/<int:pk>/delete/', views.delete_record, name='delete_record'),
]