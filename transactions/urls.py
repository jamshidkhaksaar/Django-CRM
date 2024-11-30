from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='list'),
    path('create/', views.TransactionCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='detail'),
    path('<int:pk>/approve/', views.TransactionApproveView.as_view(), name='approve'),
    path('<int:pk>/reject/', views.TransactionRejectView.as_view(), name='reject'),
] 