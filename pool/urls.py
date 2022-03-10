from django.urls import path,include
from . import views
from rest_framework.authtoken.views import obtain_auth_token






urlpatterns = [
    path('create_user', views.createUser , name = "create-user"),
    path('login' ,views.login ),
    path('create_board/<token>' , views.create_board),
    path('addUserToBoard/<token>/<box_pk>/<board_number>' , views.addUserToBox),
    path('show_board/<token>/<board_number>' , views.show_board),
    path('verifyBox/<token>/<box_id>/<board_number>', views.verifyBox),
    path('show_board_with_code/<code>', views.show_board_with_code),
    path('show_board_with_name/<name>', views.show_board_with_name),
    path('validate_code/<code>',views.validate_code),
    path('validateName/<name>',views.validate_name),
    path('get_user_name/<pk>',views.get_user_name),
    path('leaderboard/<board_pk>',views.leaderboard),
    path('validate_creator/<token>/<board_number>', views.validate_creator),
    path('userboard/<token>',views.getBoardFromUser),
    path('game_in_progress/<board_number>',views.game_in_progress),
    path('getPriceOfBox/<board_number>',views.price_per_box),
    path('addDate',views.insertDatesForMarchMadness),
    path('moneyOwed/<boardPk>', views.get_money_owed),
    path('totalBoxes/<board_number>',views.totalBoxesLeft)




]
