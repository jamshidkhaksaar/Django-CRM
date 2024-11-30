from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', LogoutView.as_view(next_page='website:home'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('records/', views.RecordListView.as_view(), name='all_records'),
    path('records/balance/', views.BalanceRecordListView.as_view(), name='balance_entries'),
    path('records/income/', views.IncomeRecordListView.as_view(), name='income_records'),
    path('records/expense/', views.ExpenseRecordListView.as_view(), name='expense_records'),
    path('records/advance/', views.AdvanceRecordListView.as_view(), name='advance_records'),
    path('my-records/', views.MyRecordListView.as_view(), name='my_records'),
    path('approved-records/', views.ApprovedRecordListView.as_view(), name='approved_records'),
    path('rejected-records/', views.RejectedRecordListView.as_view(), name='rejected_records'),
    path('pending-records/', views.PendingRecordListView.as_view(), name='pending_records'),
    path('record/<int:pk>/', views.record_detail, name='record_detail'),
    path('record/<int:pk>/approve/', views.record_approval, name='record_approval'),
    path('record/add/', views.add_record, name='add_record'),
    path('record/<int:pk>/edit/', views.edit_record, name='edit_record'),
    path('record/<int:pk>/repay/', views.advance_repayment, name='advance_repayment'),
    path('record/<int:pk>/payable-repay/', views.payable_repayment, name='payable_repayment'),
    path('record/payback/', views.record_payback, name='record_payback'),
    path('record/<int:record_id>/installments/', views.record_installments, name='record_installments'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_as_read, name='mark_all_notifications_read'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/add/', views.UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:pk>/permissions/', views.UserPermissionsView.as_view(), name='user_permissions'),
    path('activity/', views.UserActivityListView.as_view(), name='activity_list'),
    path('record/<int:pk>/forward/', views.forward_to_deputy, name='forward_to_deputy'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/password/', views.password_change, name='password_change'),
    path('delete-all-records/', views.delete_all_records, name='delete_all_records'),
]