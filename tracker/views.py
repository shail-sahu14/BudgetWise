from django.shortcuts import render, get_object_or_404,HttpResponse,redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.conf import settings
from tracker.models import Transaction,RecurringTransaction
from tracker.filters import TransactionFilter
from tracker.forms import TransactionForm,RecurringTransactionForm,BudgetForm
from django_htmx.http import retarget
from tracker.charting import plot_income_expenses_bar_chart, plot_category_pie_chart,plot_income_expense_line_chart
from tracker.resources import TransactionResource
from tablib import Dataset
from tracker.utils import process_recurring_transactions,get_budget_summary
from django.utils import timezone
from django.contrib import messages
from datetime import date

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        process_recurring_transactions(request.user)
        alerts = get_budget_summary(request.user)['alerts']
        context = {'alerts' : alerts}
        return render(request, 'tracker/index.html',context)
    return render(request, 'tracker/index.html',{})


@login_required
def transactions_list(request):
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )
    paginator = Paginator(transaction_filter.qs, settings.PAGE_SIZE)
    transaction_page = paginator.page(1) 
    
    total_income = transaction_filter.qs.get_total_income()
    total_expenses = transaction_filter.qs.get_total_expenses()
    total_transactions = transaction_filter.qs.count()
    context = {
        'transactions': transaction_page,
        'filter': transaction_filter,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_transactions':total_transactions,
        'net_income': total_income - total_expenses
    }

    if request.htmx:
        return render(request, 'tracker/partials/transactions-container.html', context)
    
    return render(request, 'tracker/transactions-list.html', context)

@login_required
def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            context = {'message': "Transaction was added successfully!"}
            return render(request, 'tracker/partials/transaction-success.html', context)
        else:
            context = {'form': form}
            response = render(request, 'tracker/partials/create-transaction.html', context)
            return retarget(response, '#transaction-block')

    context = {'form': TransactionForm()}
    return render(request, 'tracker/partials/create-transaction.html', context)

@login_required
def update_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save()
            context = {'message': "Transaction was updated successfully!"}
            return render(request, 'tracker/partials/transaction-success.html', context)
        else:
            context = {
                'form': form,
                'transaction': transaction,
            }
            response = render(request, 'tracker/partials/update-transaction.html', context)
            return retarget(response, '#transaction-block')
        
    context = {
        'form': TransactionForm(instance=transaction),
        'transaction': transaction,
    }
    return render(request, 'tracker/partials/update-transaction.html', context)

@login_required
@require_http_methods(["DELETE"])
def delete_transaction(request,pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    context = {
        'message': f"Transaction of {transaction.amount} on {transaction.date} was deleted successfully!"
    }
    return render(request, 'tracker/partials/transaction-success.html', context)

@login_required
def get_transactions(request):
    import time
    time.sleep(1)
    page = request.GET.get('page', 1)  
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )
    paginator = Paginator(transaction_filter.qs, settings.PAGE_SIZE)
    context = {
        'transactions': paginator.page(page)
    }
    return render(
        request,
        'tracker/partials/transactions-container.html#transaction_list',
        context
    )
    
def transaction_charts(request):
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )
    
    income_expense_bar = plot_income_expenses_bar_chart(transaction_filter.qs)
    
    category_income_pie = plot_category_pie_chart(
        transaction_filter.qs.filter(type='income')
    )
    
    category_expense_pie = plot_category_pie_chart(
        transaction_filter.qs.filter(type='expense')
    )
    
    income_expense_line_chart = plot_income_expense_line_chart(transaction_filter.qs)
    
    context = {
        'filter': transaction_filter,
        'income_expense_barchart': income_expense_bar.to_html(),
        'category_income_pie': category_income_pie.to_html(),
        'category_expense_pie': category_expense_pie.to_html(),
        'income_expense_line_chart':income_expense_line_chart.to_html()
    }

    if request.htmx:
        return render(request, 'tracker/partials/charts-container.html', context)
    return render(request, 'tracker/charts.html', context)

@login_required
def export(request):
    if request.htmx:
        return HttpResponse(headers={'HX-Redirect': request.get_full_path()})
    
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )

    data = TransactionResource().export(transaction_filter.qs)
    response = HttpResponse(data.csv)
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    return response

@login_required
def import_transactions(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        resource = TransactionResource()
        dataset = Dataset()
        dataset.load(file.read().decode(), format='csv')
        result = resource.import_data(dataset, user=request.user, dry_run=True)

        # for row in result:
        #     for error in row.errors:
        #         print(error)

        if not result.has_errors():
            resource.import_data(dataset, user=request.user, dry_run=False)
            context = {'message': f'{len(dataset)} transactions were uploaded successfully'}
        else:
            context = {'message': 'Sorry, an error occurred.'}
        return render(request, 'tracker/partials/transaction-success.html', context)
    return render(request, 'tracker/partials/import-transaction.html')

@login_required
def advanced_features(request):
    context = {}
    return render(request,'tracker/features.html',context)

@login_required
def recurring_transactions(request):
    transactions = RecurringTransaction.objects.filter(user=request.user)
    context = {'transactions' : transactions}
    if request.htmx:
        return render(request, 'tracker/recurring/partials/list.html', context)
    return render(request,'tracker/recurring/recurring-transactions.html',context)

@login_required
def create_recurring_transaction(request):
    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST)
        if form.is_valid():
            recurring = form.save(commit=False)
            recurring.user = request.user
            recurring.start_date = timezone.now().date()
            recurring.next_run = timezone.now().date()
            recurring.save()
            
            return redirect('recurring')
        else:
            context = {'form': form,'is_update': False}
            response = render(request, 'tracker/recurring/create-recurring-transactions.html', context)
            return retarget(response, 'recurring-list')
    
    context = {'form': RecurringTransactionForm(),'is_update': False}
    return  render(request, 'tracker/recurring/partials/create.html', context)

@login_required
def update_recurring_transaction(request, pk):
    transaction = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save()
            context = {'message': "Transaction was updated successfully!"}
            return render(request, 'tracker/recurring/partials/success.html', context)
        else:
            context = {
                'form': form,
                'transaction': transaction,
                'is_update': True,
            }
            response = render(request, 'tracker/recurring/partials/create.html', context)
            return retarget(response, 'recurring-list')
        
    context = {
        'form': RecurringTransactionForm(instance=transaction),
        'transaction': transaction,
        'is_update': True,
    }
    return  render(request, 'tracker/recurring/partials/create.html', context)

@login_required
@require_http_methods(["DELETE"])
def delete_recurring_transaction(request,pk):
    transaction = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
    transaction.delete()

    context = {
        'message': f"Transaction of {transaction.amount} on {transaction.start_date} was deleted successfully!",
    }
    return render(request, 'tracker/recurring/partials/success.html', context)

@login_required
def budgets(request):
    summary = get_budget_summary(request.user)['summary']
    context = {'totals': summary[0],'summary': summary[1:]}
    return render(request, 'tracker/budget-summary.html',context)

def edit_budgets(request):
    month = date.today().replace(day=1)

    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user, month=month)
        if form.is_valid():
            form.save()
            messages.success(request, "Budgets saved successfully!")
            return redirect('budgets')  
    else:
        form = BudgetForm(user=request.user, month=month)

    return render(request, 'tracker/budgets/edit-budget.html', {'form': form})


