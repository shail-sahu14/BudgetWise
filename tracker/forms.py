from django import forms
from tracker.models import Transaction, Category,RecurringTransaction , Budget
from datetime import date

class TransactionForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.RadioSelect()
    )

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive number")
        return amount
    
    class Meta:
        model = Transaction
        fields = (
            'type',
            'amount',
            'date',
            'category',       
        )
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class RecurringTransactionForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.RadioSelect()
    )

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive number")
        return amount

    class Meta:
        model = RecurringTransaction
        fields = (
            'type',
            'amount',
            'frequency',
            'category',
        )
        
class BudgetForm(forms.Form):
    def __init__(self, *args, user=None, month=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.month = month or date.today().replace(day=1)

        categories = Category.objects.all()

        for category in categories:
            existing = Budget.objects.filter(user=user, category=category, month=self.month).first()
            initial = existing.amount if existing else 0
            self.fields[f'category_{category.id}'] = forms.DecimalField(
                label=category.name,
                initial=initial,
                decimal_places=2,
                required=False
            )

    def save(self):
        for name, value in self.cleaned_data.items():
            if not value:
                continue
            if name.startswith('category_'):
                cat_id = int(name.split('_')[1])
                category = Category.objects.get(id=cat_id)
                Budget.objects.update_or_create(
                    user=self.user,
                    category=category,
                    month=self.month,
                    defaults={'amount': value}
                )
