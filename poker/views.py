from django.shortcuts import render, redirect, get_object_or_404
from tables.models import Table
import threading
from .poker import main
from django.contrib.auth.decorators import login_required

@login_required
def game(request, pk):
    table = get_object_or_404(Table, pk=pk)
    if request.user.money >= table.buyIn and table.getNoOfPlayers() < table.maxNoOfPlayers:
        pokerThread = threading.Thread(target=main, args=(pk, request.user.username), daemon=True)
        pokerThread.start()
        context = {
            'table': table,
        }
        return render(request, 'game.html', context)
    return redirect('index')