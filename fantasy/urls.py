from django.urls import path

from . import views

urlpatterns = [
    path("tournaments/", views.TournamentListCreate.as_view()),
    path("tournaments/<int:pk>/", views.TournamentDetail.as_view()),
    path("tournaments/<int:pk>/players/", views.PlayerList.as_view()),
    path("tournaments/<int:pk>/players/upload/", views.PlayerUploadView.as_view()),
    path("tournaments/<int:pk>/stats/upload/", views.StatsUploadView.as_view()),
    path("tournaments/<int:pk>/teams/", views.TeamListCreate.as_view()),
    path("tournaments/<int:pk>/leaderboard/", views.LeaderboardView.as_view()),
    path("teams/<int:pk>/", views.TeamDetail.as_view()),
]