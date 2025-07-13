from django.contrib import admin
from tracker.models import User,Category, Transaction,RecurringTransaction,Budget

# Register your models here.
admin.site.register(User)
admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(RecurringTransaction)
admin.site.register(Budget)