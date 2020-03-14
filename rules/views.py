from django.shortcuts import render

def pokerRules(request):
    return render(request, 'how-to-play.html')