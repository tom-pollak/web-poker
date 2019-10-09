from rest_framework import serializers
from .models import Table
from poker.models import Room

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['noOfPlayers']

class TableSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True, required=False)

    class Meta:
        model = Table
        fields = ['name', 'room', 'maxNoOfPlayers']