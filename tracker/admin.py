from django.contrib import admin
from tracker.models import Category, Transaction,RecurringTransaction

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(RecurringTransaction)