from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from .scoring import multiplier_for_seed


class Tournament(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        LOCKED = "locked", "Locked"
        COMPLETE = "complete", "Complete"

    name = models.CharField(max_length=120)
    year = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    # Entries close automatically at this time (optional). An admin can also lock manually.
    lock_at = models.DateTimeField(null=True, blank=True)
    roster_size = models.PositiveSmallIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "-id"]

    def __str__(self):
        return f"{self.name} ({self.year})"

    @property
    def is_open(self) -> bool:
        if self.status != self.Status.OPEN:
            return False
        return not (self.lock_at and timezone.now() >= self.lock_at)

    @property
    def phase(self) -> str:
        """What the UI should show: 'open', 'locked' or 'complete'."""
        if self.status == self.Status.OPEN and not self.is_open:
            return self.Status.LOCKED
        return self.status


class PlayerQuerySet(models.QuerySet):
    def with_stats(self):
        return self.annotate(
            games_played=Count("game_stats", distinct=True),
            raw_points=Coalesce(Sum("game_stats__points"), 0),
        )


class Player(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="players")
    external_id = models.CharField(max_length=120)
    name = models.CharField(max_length=120)
    school = models.CharField(max_length=120)
    seed = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(16)])
    position = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=40, blank=True)

    objects = PlayerQuerySet.as_manager()

    class Meta:
        ordering = ["seed", "school", "name"]
        constraints = [
            models.UniqueConstraint(fields=["tournament", "external_id"], name="uniq_player_per_tournament"),
        ]

    def __str__(self):
        return f"{self.name} ({self.school}, #{self.seed})"

    @property
    def multiplier(self) -> int:
        return multiplier_for_seed(self.seed)


class PlayerGameStat(models.Model):
    """One row per player per game. The number of rows is the number of games played."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="game_stats")
    round_label = models.CharField(max_length=40)  # e.g. "Round of 64"
    points = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["player", "round_label"], name="uniq_stat_per_round"),
        ]

    def __str__(self):
        return f"{self.player.name} - {self.round_label}: {self.points}"


class FantasyTeam(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fantasy_teams")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="teams")
    name = models.CharField(max_length=80, blank=True)
    players = models.ManyToManyField(Player, related_name="teams")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name or 'Team'} ({self.user})"

# Create your models here.
