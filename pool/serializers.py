
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    Board,
    Admin,
    GeneratedNumbers,
    NFL,
    MarchMadness,
    Winnings,
    Box,
    MarchMadnessDates,
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    email = serializers.EmailField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
        ]

    def validate_email(self, value):
        value = value.lower().strip()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        ]
        read_only_fields = fields


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = [
            "id",
            "code",
            "type",
            "name",
            "box_price",
        ]


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = [
            "id",
            "user_pk",
            "board_number",
            "creator",
        ]


class GeneratedNumbersSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedNumbers
        fields = ["id", "winning", "losing"]


class NFLSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFL
        fields = [
            "id",
            "one",
            "two",
            "three",
            "four",
            "board_number",
            "box_price",
        ]


class MarchMadnessSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarchMadness
        fields = [
            "id",
            "first_round",
            "second_round",
            "sweet_sixteen",
            "elite_eight",
            "final_four",
            "championship",
            "board_number",
            "box_price",
        ]


class WinningsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Winnings
        fields = [
            "id",
            "user_pk",
            "balance",
            "username",
            "board_pk",
            "first_name",
        ]


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = [
            "id",
            "pair",
            "board_number",
            "user_pk",
            "username",
            "balance",
            "hit",
            "count",
            "first_name",
        ]


class MarchMadnessDatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarchMadnessDates
        fields = ["id", "date", "visited"]
