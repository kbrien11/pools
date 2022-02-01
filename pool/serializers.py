from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Board,Box,NFL,Winnings,MarchMadness,Admin,GeneratedNumbers
from django.contrib.auth import authenticate
from rest_framework import serializers


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields =['id','code','type','name','box_price']

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['id','user_pk','board_number','creator']
        
class GeneratedNumbersSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedNumbers
        fields = ['id','winning','losing']

class NFLSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFL
        fields = ['id','one','two','three','four','board_number','box_price']

class MarchMadnessSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarchMadness
        fields = ['id','first_round','second_round','sweet_sixteen','elite_eight','final_four','championship','board_number','box_price']

class WinningsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Winnings
        fields = ['id','user_pk','balance','username','board_pk','first_name']

class BoxSerialiazer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = ['id','pair','board_number','user_pk','username','balance','hit','count','first_name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {'password': {'required': False},'first_name':{'required':False},'last_name':{'required':False},'email':{'required':False}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        print(Token)
        return user


