from django.urls import path
from tracker import views


urlpatterns = [
    path("", views.index, name='index'),
    path("transactions/", views.transactions_list, name='transactions-list'),
    path('transactions/create/', views.create_transaction, name='create-transaction'),
    
    path('transactions/<int:pk>/update/', views.update_transaction, name='update-transaction'),
    path('transactions/<int:pk>/delete/', views.delete_transaction, name='delete-transaction'),
    
    path('get-transactions/', views.get_transactions, name='get-transactions'),
    path('transactions/charts', views.transaction_charts, name='transactions-charts'),
    
    path('transactions/export', views.export, name='export'),
    path('transactions/import', views.import_transactions, name='import'),
    
    path('features/', views.advanced_features, name='features'),
    path('features/recurring/',views.recurring_transactions,name='recurring'),
    path('features/recurring/create/', views.create_recurring_transaction, name='create-recurring-transaction'),
    path('features/recurring/<int:pk>/update/', views.update_recurring_transaction, name='update-recurring-transaction'),
    path('features/recurring/<int:pk>/delete/', views.delete_recurring_transaction, name='delete-recurring-transaction'),
    
    path('budget_summary/',views.budgets,name='budgets'),
    path('budget_summary/edit',views.edit_budgets,name='edit-budgets'),
]