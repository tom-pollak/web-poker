from django.shortcuts import render
from django.db import close_old_connections


def pokerRules(request):
    close_old_connections()
    return render(request, 'how-to-play.html')
