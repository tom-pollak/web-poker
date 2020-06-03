from django.shortcuts import render, redirect
from tables.models import Table
from django.contrib.auth.decorators import login_required
from .forms import TableForm
from django.db import close_old_connections


def index(request):
    close_old_connections()
    tables = Table.objects.all()
    context = {
        'tables': tables
    }
    close_old_connections()
    return render(request, 'index.html', context)


@login_required
def resetMoney(request):
    close_old_connections()
    if request.user.money < 1000:
        print('reset')
        request.user.money = 1000
        request.user.save()
        close_old_connections()
        return redirect('index')
    else:
        print('ERROR attempted reset')
        close_old_connections()
        return redirect('index')


@login_required
def createTable(request):
    close_old_connections()
    # user submitting the form
    if request.method == 'POST':
        # gets form submission based on the POST request
        form = TableForm(request.POST)
        if form.is_valid():
            # saves form as Table model
            table = form.save()
            close_old_connections()
            return redirect('game', pk=table.pk)

    # user GETting the form
    elif request.method == 'GET':
        form = TableForm()

    context = {'form': form}
    close_old_connections()
    return render(request, 'table-form.html', context)
