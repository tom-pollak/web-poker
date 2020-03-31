from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render
from .models import CustomUser
from .forms import CustomUserCreationForm

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm #variables must be underscores
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

def profile(request, username):
    player = CustomUser.objects.get(username=username)
    context = {
        'player': player
    }
    return render(request, 'profile.html', context)