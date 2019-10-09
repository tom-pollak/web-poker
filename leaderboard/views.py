from django.shortcuts import render
from accounts.models import CustomUser

def leaderboard(request):
    users = CustomUser.objects.filter().values('username', 'money').order_by('-money')
    context = {
        'users': users
    }
    
    return render(request, 'leaderboard.html', context)