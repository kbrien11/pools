from rest_framework import serializers

from .models import FantasyTeam, Player, Tournament


class TournamentSerializer(serializers.ModelSerializer):
    is_open = serializers.BooleanField(read_only=True)
    phase = serializers.CharField(read_only=True)
    player_count = serializers.SerializerMethodField()
    team_count = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = [
            "id", "name", "year", "status", "phase", "is_open",
            "lock_at", "roster_size", "player_count", "team_count",
        ]

    def get_player_count(self, obj):
        return obj.players.count()

    def get_team_count(self, obj):
        return obj.teams.count()


class PlayerSerializer(serializers.ModelSerializer):
    multiplier = serializers.IntegerField(read_only=True)
    games_played = serializers.SerializerMethodField()
    raw_points = serializers.SerializerMethodField()
    total_points = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = [
            "id", "external_id", "name", "school", "seed", "position", "region",
            "multiplier", "games_played", "raw_points", "total_points",
        ]

    # These come from Player.objects.with_stats(); always annotate before serializing.
    def get_games_played(self, obj):
        return getattr(obj, "games_played", 0)

    def get_raw_points(self, obj):
        return getattr(obj, "raw_points", 0)

    def get_total_points(self, obj):
        return getattr(obj, "raw_points", 0) * obj.multiplier


class TeamSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True, max_length=80)
    username = serializers.CharField(source="user.username", read_only=True)
    tournament_id = serializers.IntegerField(read_only=True)
    tournament_name = serializers.CharField(source="tournament.name", read_only=True)
    is_mine = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    total_points = serializers.SerializerMethodField()
    players = serializers.SerializerMethodField()
    player_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = FantasyTeam
        fields = [
            "id", "name", "username", "tournament_id", "tournament_name",
            "is_mine", "can_edit", "total_points", "players", "player_ids",
        ]

    def _scored_players(self, obj):
        if not hasattr(obj, "_scored_players"):
            players = list(Player.objects.filter(teams=obj).with_stats())
            players.sort(key=lambda p: (-(p.raw_points * p.multiplier), p.name))
            obj._scored_players = players
        return obj._scored_players

    def get_players(self, obj):
        return PlayerSerializer(self._scored_players(obj), many=True).data

    def get_total_points(self, obj):
        return sum(p.raw_points * p.multiplier for p in self._scored_players(obj))

    def get_is_mine(self, obj):
        request = self.context.get("request")
        return bool(request and obj.user_id == request.user.id)

    def get_can_edit(self, obj):
        return self.get_is_mine(obj) and obj.tournament.is_open

    def validate(self, attrs):
        tournament = self.instance.tournament if self.instance else self.context["tournament"]
        ids = attrs.get("player_ids")

        if ids is not None:
            size = tournament.roster_size
            if len(ids) != size:
                raise serializers.ValidationError({"player_ids": f"Pick exactly {size} players."})
            if len(set(ids)) != len(ids):
                raise serializers.ValidationError({"player_ids": "Each player can only be picked once."})

            players = list(Player.objects.filter(tournament=tournament, id__in=ids))
            if len(players) != len(ids):
                raise serializers.ValidationError({"player_ids": "One or more players aren't in this tournament."})
            attrs["_players"] = players

        return attrs

    def create(self, validated_data):
        players = validated_data.pop("_players")
        validated_data.pop("player_ids", None)

        if not (validated_data.get("name") or "").strip():
            count = FantasyTeam.objects.filter(
                user=validated_data["user"], tournament=validated_data["tournament"]
            ).count()
            validated_data["name"] = f"Team {count + 1}"

        team = FantasyTeam.objects.create(**validated_data)
        team.players.set(players)
        return team

    def update(self, instance, validated_data):
        players = validated_data.pop("_players", None)
        validated_data.pop("player_ids", None)

        if "name" in validated_data:
            instance.name = validated_data["name"].strip() or instance.name
            instance.save()
        if players is not None:
            instance.players.set(players)
        return instance