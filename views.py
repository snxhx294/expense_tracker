from django.shortcuts import render, redirect
from .models import Expense
from .forms import ExpenseForm
from django.db.models import Sum
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

@login_required
def expense_list(request):
    expenses = Expense.objects.order_by('-date')
    return render(request, 'expenses/expense_list.html', {'expenses': expenses})

@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
        
    return render(request, 'expenses/add_expense.html', {'form': form})

@login_required
def delete_expense(request, expense_id):
    expense = Expense.objects.get(id=expense_id)
    if expense:
        expense.delete()
    return redirect('expense_list')

@login_required
def expense_list(request):
    category_filter = request.GET.get('category', '')  # Get selected category from URL
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    
    if category_filter:
        expenses = expenses.filter(category=category_filter)  # Filter expenses by category

    categories = Expense.objects.values_list('category', flat=True).distinct()  # Get unique categories

    return render(request, 'expenses/expense_list.html', {
        'expenses': expenses,
        'categories': categories,
    })

@login_required
def expense_chart(request):
    # Map internal category keys to display labels
    category_display = dict(Expense.CATEGORY_CHOICES)

    # Aggregate total amount by category key
    data = (
        Expense.objects.filter(user=request.user)
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('category')
    )

    # Replace category keys with their display labels
    categories = [category_display[item['category']] for item in data]
    totals = [float(item['total']) for item in data]

    context = {
        'categories': json.dumps(categories),
        'totals': json.dumps(totals),
    }

    return render(request, 'expenses/expense_chart.html', context)

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('expense_list')  # or any default landing page
        else:
            return render(request, 'expenses/login.html', {'error': 'Invalid credentials'})

    return render(request, 'expenses/login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


    