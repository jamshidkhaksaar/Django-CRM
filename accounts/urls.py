from django.urls import path
from . import views

 # Add this to your existing urlpatterns
 path('dashboard/', views.dashboard, name='dashboard'),
 
urlpatterns = [
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/create/', views.create_transaction, name='create_transaction'),
    path('transactions/<int:pk>/approve/', views.approve_transaction, name='approve_transaction'),
]
