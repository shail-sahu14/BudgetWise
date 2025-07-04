from tracker.models import RecurringTransaction , Transaction
from datetime import date, timedelta

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
