from django.shortcuts import render, redirect
from tables.models import Table
from poker.models import Room
from django.contrib.auth.decorators import login_required
from .forms import TableForm

def index(request):
    tables = Table.objects.all()
    context = {
        'tables': tables
    }
    return render(request, 'index.html', context)

@login_required
def resetMoney(request):
    if request.user.money < 1000:
        print('reset')
        request.user.money = 1000
        request.user.save()
        return redirect('index')
    else:
        print('ERROR attempted reset')
        return redirect('index')

@login_required
def createTable(request):
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save()
            return redirect('game', pk=table.pk)
    else:
        form = TableForm()

    context = {
        'form': form
    }

    return render(request, 'tableForm.html', context)