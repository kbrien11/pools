from django.urls import path
from . import views


urlpatterns = [
    # Authentication
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.login, name="login"),
    path("auth/logout/", views.logout, name="logout"),

    # Pools / boards
    path("pools/", views.pools, name="pools"),
    path("pools/<int:pool_id>/", views.pool_detail, name="pool-detail"),
    path("pools/join/", views.join_pool, name="join-pool"),

    # Boxes
    path(
        "pools/<int:pool_id>/boxes/",
        views.pool_boxes,
        name="pool-boxes",
    ),
    path(
        "pools/<int:pool_id>/boxes/claim/",
        views.claim_boxes,
        name="claim-boxes",
    ),
    path(
        "pools/<int:pool_id>/boxes/<int:box_id>/verify/",
        views.verify_box,
        name="verify-box",
    ),
    path(
        "pools/<int:pool_id>/boxes/remaining/",
        views.remaining_boxes,
        name="remaining-boxes",
    ),

    # Board status
    path(
        "pools/<int:pool_id>/status/",
        views.pool_status,
        name="pool-status",
    ),

    # Leaderboard / winnings
    path(
        "pools/<int:pool_id>/leaderboard/",
        views.leaderboard,
        name="leaderboard",
    ),
    path(
        "pools/<int:pool_id>/winnings/",
        views.user_winnings,
        name="user-winnings",
    ),
    path(
        "pools/<int:pool_id>/money-owed/",
        views.money_owed,
        name="money-owed",
    ),

    # Board configuration
    path(
        "pools/<int:pool_id>/creator/",
        views.validate_creator,
        name="validate-creator",
    ),
    path(
        "pools/<int:pool_id>/numbers/",
        views.get_board_numbers,
        name="board-numbers",
    ),
    path(
        "pools/<int:pool_id>/payout/",
        views.get_board_payout,
        name="board-payout",
    ),
]