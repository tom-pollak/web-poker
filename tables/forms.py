from django import forms
from .models import Table

class TableForm(forms.ModelForm):

    class Meta:
        #specifys what model to use
        model = Table
        
        #fields from Table model included in form
        fields = ('name', 'buyIn', 'maxNoOfPlayers')

        #read friendly names
        labels = {
            'name': 'Name',
            'buyIn': 'Buy in',
            'maxNoOfPlayers': 'Maximum number of players'
        }