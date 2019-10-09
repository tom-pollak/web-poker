from django.shortcuts import render, redirect
from tables.models import Table
from poker.models import Room
import json
import threading
from .poker import main
from django.contrib.auth.decorators import login_required

@login_required
def game(request, pk):
    table = Table.objects.get(pk=pk)
    tableGroup = 'table_' + str(pk)
    if request.user.money >= table.buyIn and table.getNoOfPlayers() < table.maxNoOfPlayers:
        pokerThread = threading.Thread(target=main, args=(pk, request.user.username), daemon=True)
        pokerThread.start()
        context = {
            'table': table,
        }
        return render(request, 'game.html', context)
    return redirect('index')