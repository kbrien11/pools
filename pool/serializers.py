from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Board,Box,NFL,Winnings,MarchMadness,Admin
from django.contrib.auth import authenticate
from rest_framework import serializers


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields =['id','code','type']

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['id','user_pk','board_number','creator']

class NFLSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFL
        fields = ['id','one','two','three','four','board_number']

class MarchMadnessSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarchMadness
        fields = ['id','first_round','second_round','sweet_sixteen','elite_eight','final_four','championship','board_number']

class WinningsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Winnings
        fields = ['id','user_pk','balance','username','board_pk']

class BoxSerialiazer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = ['id','pair','board_number','user_pk','username','balance','hit','count']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True, 'required': False},'first_name':{'required':False},'last_name':{'required':False},'email':{'required':False}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        print(Token)
        return user


