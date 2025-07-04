import plotly.express as px
from django.db.models import Sum
from tracker.models import Category

import plotly.express as px
import plotly.graph_objects as go
from django.db.models import Sum
from tracker.models import Category

def plot_income_expenses_bar_chart(qs):
    x_vals = ['Income', 'Expenditure']

    total_income = qs.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = qs.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0

    fig = px.bar(
        x=x_vals,
        y=[total_income, total_expenses],
        color=x_vals,
        color_discrete_sequence=['#4dd599', '#f67280']  # Mint green and coral pink
    )

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title_text='Income vs Expenditure',
        title_font_size=20
    )

    fig.update_xaxes(showgrid=False, color='white')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.2)', color='white')

    return fig


def plot_category_pie_chart(qs):
    count_per_category = (
        qs.order_by('category').values('category')
        .annotate(total=Sum('amount'))
    )
    category_pks = count_per_category.values_list('category', flat=True).order_by('category')
    categories = Category.objects.filter(pk__in=category_pks).order_by('pk').values_list('name', flat=True)
    total_amounts = count_per_category.order_by('category').values_list('total', flat=True)

    fig = px.pie(
        values=total_amounts,
        names=categories,
        color_discrete_sequence=px.colors.sequential.Tealgrn  # Aqua/green gradient palette
    )

    fig.update_layout(
        title_text="Total Amount per Category",
        title_font_size=20,
        font=dict(color='white'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def plot_income_expense_line_chart(qs):
    # Prepare the queryset
    data = qs.values('date', 'amount', 'type')

    # Create the line chart
    fig = px.line(
        data,
        x='date',
        y='amount',
        color='type',
        color_discrete_map={
            'income': '#4dd599',   # Mint green
            'expense': '#f67280'   # Coral pink
        },
        title='Income and Expenses Over Time',
        labels={'date': 'Date', 'amount': 'Amount'},
        template='plotly_dark'
    )

    # Style the layout to match your gradient background
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title_font_size=20,
        hovermode='x unified'
    )

    fig.update_xaxes(showgrid=False, color='white')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.2)', color='white')

    return fig
