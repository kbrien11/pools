import json

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import SAFE_METHODS, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FantasyTeam, Player, PlayerGameStat, Tournament
from .serializers import PlayerSerializer, TeamSerializer, TournamentSerializer


# ---------------------------------------------------------------- tournaments


class TournamentListCreate(generics.ListCreateAPIView):
    """GET: all tournaments. POST (admin): create one."""

    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    pagination_class = None

    def get_permissions(self):
        return [IsAdminUser()] if self.request.method == "POST" else [IsAuthenticated()]


class TournamentDetail(generics.RetrieveUpdateAPIView):
    """GET: one tournament. PATCH (admin): rename, change status, set lock time."""

    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

    def get_permissions(self):
        return [IsAuthenticated()] if self.request.method in SAFE_METHODS else [IsAdminUser()]


# -------------------------------------------------------------------- players


class PlayerList(generics.ListAPIView):
    """Every eligible player for a tournament, with seed multiplier and points so far."""

    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return (
            Player.objects.filter(tournament_id=self.kwargs["pk"])
            .with_stats()
            .order_by("seed", "school", "name")
        )


def _load_rows(request, key):
    """Accept either a JSON body or a multipart upload with a `file` field."""
    upload = request.FILES.get("file")
    if upload:
        try:
            data = json.load(upload)
        except ValueError:
            raise ValidationError({"errors": ["That file isn't valid JSON."]})
    else:
        data = request.data

    rows = data.get(key) if isinstance(data, dict) else data
    if not isinstance(rows, list) or not rows:
        raise ValidationError({"errors": [f'Expected a non-empty list under "{key}".']})
    return rows


class PlayerUploadView(APIView):
    """
    Admin: upload the eligible player list.

    {"players": [{"external_id": "duke-001", "name": "...", "school": "Duke",
                  "seed": 1, "position": "G", "region": "East"}]}

    Re-uploading is safe: players are matched on external_id and updated.
    The whole upload is rejected if any row is invalid.
    """

    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        rows = _load_rows(request, "players")

        errors, clean, seen = [], [], set()
        for i, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                errors.append(f"Row {i}: expected an object.")
                continue

            name = str(row.get("name") or "").strip()
            school = str(row.get("school") or "").strip()
            try:
                seed = int(row.get("seed"))
            except (TypeError, ValueError):
                seed = None

            if not name or not school or seed is None or not 1 <= seed <= 16:
                errors.append(f"Row {i}: needs a name, a school and a seed from 1 to 16.")
                continue

            external_id = str(row.get("external_id") or f"{school}:{name}").strip()
            if external_id in seen:
                errors.append(f"Row {i}: duplicate external_id '{external_id}'.")
                continue
            seen.add(external_id)

            clean.append({
                "external_id": external_id,
                "defaults": {
                    "name": name,
                    "school": school,
                    "seed": seed,
                    "position": str(row.get("position") or "").strip(),
                    "region": str(row.get("region") or "").strip(),
                },
            })

        if errors:
            raise ValidationError({"errors": errors[:20]})

        created = updated = 0
        with transaction.atomic():
            for item in clean:
                _, was_created = Player.objects.update_or_create(
                    tournament=tournament,
                    external_id=item["external_id"],
                    defaults=item["defaults"],
                )
                created += was_created
                updated += not was_created

        return Response({"created": created, "updated": updated})


class StatsUploadView(APIView):
    """
    Admin: upload per-game points as the tournament plays out.

    {"games": [{"external_id": "duke-001", "round": "Round of 64", "points": 22}]}

    One row per player per game. Re-uploading the same (player, round) overwrites it.
    """

    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        rows = _load_rows(request, "games")
        players = {p.external_id: p for p in Player.objects.filter(tournament=tournament)}

        errors, clean, seen = [], [], set()
        for i, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                errors.append(f"Row {i}: expected an object.")
                continue

            external_id = str(row.get("external_id") or "").strip()
            round_label = str(row.get("round") or "").strip()
            try:
                points = int(row.get("points"))
            except (TypeError, ValueError):
                points = None

            if external_id not in players:
                errors.append(f"Row {i}: unknown player '{external_id}'.")
            elif not round_label or points is None or points < 0:
                errors.append(f"Row {i}: needs a round and a non-negative points value.")
            elif (external_id, round_label) in seen:
                errors.append(f"Row {i}: duplicate entry for '{external_id}' in '{round_label}'.")
            else:
                seen.add((external_id, round_label))
                clean.append((players[external_id], round_label, points))

        if errors:
            raise ValidationError({"errors": errors[:20]})

        created = updated = 0
        with transaction.atomic():
            for player, round_label, points in clean:
                _, was_created = PlayerGameStat.objects.update_or_create(
                    player=player, round_label=round_label, defaults={"points": points}
                )
                created += was_created
                updated += not was_created

        return Response({"created": created, "updated": updated})


# ---------------------------------------------------------------------- teams


class TeamListCreate(generics.ListCreateAPIView):
    """GET: my teams in this tournament. POST: submit a new team (any number allowed)."""

    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return FantasyTeam.objects.filter(
            tournament_id=self.kwargs["pk"], user=self.request.user
        ).select_related("user", "tournament")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["tournament"] = get_object_or_404(Tournament, pk=self.kwargs["pk"])
        return context

    def perform_create(self, serializer):
        tournament = serializer.context["tournament"]
        if not tournament.is_open:
            raise PermissionDenied("Entries are closed for this tournament.")
        serializer.save(user=self.request.user, tournament=tournament)


class TeamDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: owner any time; everyone else only once entries close (rosters stay hidden until then).
    PUT/PATCH/DELETE: owner only, and only while entries are open.
    """

    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    queryset = FantasyTeam.objects.select_related("user", "tournament")

    def get_object(self):
        team = super().get_object()
        is_owner = team.user_id == self.request.user.id

        if self.request.method in SAFE_METHODS:
            if not is_owner and team.tournament.is_open:
                raise PermissionDenied("Rosters are hidden until entries close.")
        else:
            if not is_owner:
                raise PermissionDenied("You can only change your own teams.")
            if not team.tournament.is_open:
                raise PermissionDenied("Entries are closed for this tournament.")
        return team


# ---------------------------------------------------------------- leaderboard


class LeaderboardView(APIView):
    """All teams ranked by total points. Tied teams share a rank."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)

        totals = {
            p.id: p.raw_points * p.multiplier
            for p in Player.objects.filter(tournament=tournament).with_stats()
        }

        teams = (
            FantasyTeam.objects.filter(tournament=tournament)
            .select_related("user")
            .prefetch_related("players")
        )

        rows = [
            {
                "team_id": team.id,
                "team_name": team.name,
                "username": team.user.username,
                "first_name": team.user.first_name,
                "total_points": sum(totals.get(p.id, 0) for p in team.players.all()),
                "is_mine": team.user_id == request.user.id,
            }
            for team in teams
        ]
        rows.sort(key=lambda r: (-r["total_points"], r["team_name"].lower()))

        rank, previous = 0, None
        for position, row in enumerate(rows, start=1):
            if row["total_points"] != previous:
                rank, previous = position, row["total_points"]
            row["rank"] = rank

        return Response(rows)
