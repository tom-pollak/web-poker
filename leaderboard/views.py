from django.shortcuts import render
from accounts.models import CustomUser
from django.db import close_old_connections


def leaderboard(request):
    close_old_connections()
    users = CustomUser.objects.filter().values(
        'username', 'money').order_by('-money')
    context = {
        'users': users
    }
    close_old_connections()
    return render(request, 'leaderboard.html', context)
