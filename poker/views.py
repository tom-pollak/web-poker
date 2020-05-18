from django.shortcuts import render, redirect, get_object_or_404
from tables.models import Table
import threading
from .poker import main
from django.contrib.auth.decorators import login_required
from django.db import close_old_connections


@login_required
def game(request, pk):
    close_old_connections()
    table = get_object_or_404(Table, pk=pk)
    if request.user.money >= table.buyIn and table.getNoOfPlayers() < table.maxNoOfPlayers:
        pokerThread = threading.Thread(target=main, args=(
            pk, request.user.username), daemon=True)
        pokerThread.start()
        context = {
            'table': table,
        }
        close_old_connections()
        return render(request, 'game.html', context)
    close_old_connections()
    return redirect('index')
