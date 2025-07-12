from tracker.models import RecurringTransaction , Transaction, Budget
from datetime import date, timedelta
from django.db.models import Sum

def process_recurring_transactions(user):
    today = date.today()
    recs = RecurringTransaction.objects.filter(user=user, next_run__lte=today)

    for rec in recs:
        while rec.next_run <= today:
            Transaction.objects.create(
                user=user,
                amount=rec.amount,
                category=rec.category,
                type=rec.type,
                date=rec.next_run,
            )

            # Increment next_run based on frequency
            if rec.frequency == 'DAILY':
                rec.next_run += timedelta(days=1)
            elif rec.frequency == 'WEEKLY':
                rec.next_run += timedelta(weeks=1)
            elif rec.frequency == 'MONTHLY':
                if rec.next_run.month == 12:
                    rec.next_run = rec.next_run.replace(month=1, year=rec.next_run.year + 1)
                else:
                    rec.next_run = rec.next_run.replace(month=rec.next_run.month + 1)
            elif rec.frequency == 'YEARLY':
                rec.next_run = rec.next_run.replace(year=rec.next_run.year + 1)

        rec.save()

def get_budget_summary(user):
    today = date.today()
    first_of_month = today.replace(day=1)
    
    budgets = Budget.objects.filter(user=user, month=first_of_month)

    spending = (
        Transaction.objects
        .filter(user=user, date__gte=first_of_month,type='expense')
        .values('category')
        .annotate(spent=Sum('amount'))
    )
    
    spent_dict = {entry['category']: entry['spent'] for entry in spending}

    summary = []
    total_amount = 0
    total_spent = 0
    
    alerts = []
    for budget in budgets:
        category = budget.category
        spent = spent_dict.get(category.id, 0)
        percent = min((spent / budget.amount) * 100, 100) if budget.amount > 0 else 0
    
        total_spent += spent
        total_amount += budget.amount
        
        summary.append({
            'category': category.name,
            'budgeted': budget.amount,
            'spent': spent,  
            'percent': round(percent, 0)
        })
        
        if(percent >= 85):
            alerts.append({
                'category': category.name,
                'percent': round(percent, 0)
            })
    
    percent = min((total_spent / total_amount) * 100, 100) if total_amount > 0 else 0
    summary.insert(0, {
        'category': 'Totals',
        'budgeted': total_amount,
        'spent': total_spent,  
        'percent': round(percent, 0)
    })
    
    if(percent >= 85):
        alerts.insert(0,{
            'category': 'Totals',
            'percent': round(percent, 0)
        })
    

    return {
        'summary': summary,
        'alerts': alerts
    }



    

