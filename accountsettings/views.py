from django.shortcuts import render
from accounts.models import CustomUser

def profile(request, username):
    player = CustomUser.objects.get(username=username)
    context = {
        'player': player
    }
    return render(request, 'profile.html', context)