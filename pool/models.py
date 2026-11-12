from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class Board(models.Model):
    code = models.IntegerField(unique=True)
    type = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    box_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class Box(models.Model):
    user_pk = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="claimed_boxes"
    )
    pair = models.CharField(max_length=10)
    board_number = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="boxes"
    )
    username = models.CharField(max_length=42, blank=True, default="")
    first_name = models.CharField(max_length=42, blank=True, default="")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hit = models.BooleanField(default=False)
    count = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["board_number", "pair"],
                name="unique_box_pair_per_board"
            ),
            models.CheckConstraint(
                condition=Q(balance__gte=0),
                name="box_balance_nonnegative"
            ),
        ]

    def __str__(self):
        return f"{self.board_number.name} - {self.pair}"


class NFL(models.Model):
    one = models.DecimalField(max_digits=10, decimal_places=2)
    two = models.DecimalField(max_digits=10, decimal_places=2)
    three = models.DecimalField(max_digits=10, decimal_places=2)
    four = models.DecimalField(max_digits=10, decimal_places=2)
    board_number = models.OneToOneField(
        Board,
        on_delete=models.CASCADE,
        related_name="nfl_payout"
    )
    box_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class MarchMadness(models.Model):
    first_round = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    second_round = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sweet_sixteen = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    elite_eight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_four = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    championship = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    board_number = models.OneToOneField(
        Board,
        on_delete=models.CASCADE,
        related_name="march_madness_payout"
    )
    box_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Winnings(models.Model):
    user_pk = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pool_winnings"
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    username = models.CharField(max_length=42, blank=True, default="")
    first_name = models.CharField(max_length=42, blank=True, default="")
    board_pk = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="winnings"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_pk", "board_pk"],
                name="unique_user_winnings_per_board"
            )
        ]


class Admin(models.Model):
    user_pk = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pool_admin_roles"
    )
    board_number = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="admins"
    )
    creator = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_pk", "board_number"],
                name="unique_admin_per_board"
            )
        ]


class GeneratedNumbers(models.Model):
    winning = models.JSONField(default=list)
    losing = models.JSONField(default=list)
    board_pk = models.OneToOneField(
        Board,
        on_delete=models.CASCADE,
        related_name="generated_numbers"
    )


class ScrapeData(models.Model):
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)


class MarchMadnessDates(models.Model):
    date = models.DateField(unique=True)
    visited = models.BooleanField(default=False)

class PoolMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "board"],
                name="unique_pool_member",
            )
        ]