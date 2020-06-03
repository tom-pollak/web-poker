from .models import Table
from rest_framework import serializers


class TableSerializer(serializers.ModelSerializer):
    noOfPlayers = serializers.SerializerMethodField()

    class Meta:
        model = Table
        #the fields serailized
        fields = ['name', 'maxNoOfPlayers', 'noOfPlayers']
    
    def get_noOfPlayers(self, obj):
        #uses the Table method to get the no of players
        return obj.getNoOfPlayers()
