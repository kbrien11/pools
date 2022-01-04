from django.urls import path,include
from . import views
from rest_framework.authtoken.views import obtain_auth_token






urlpatterns = [
    path('create_user', views.createUser , name = "create-user"),
    path('get-user/<str:username>', views.getUser , name = 'get-user'),
    path('login' ,views.login ),
    path('create_board/<token>' , views.create_board),
    path('addUserToBoard/<token>/<box_pk>/<board_number>' , views.addUserToBox),
    path('show_board/<token>/<board_number>' , views.show_board),
    path('verifyBox/<token>/<box_id>/<board_number>', views.verifyBox),
    path('addToNFLTable/<board_number>', views.addToNFLTable),
    path('show_board_with_code/<code>', views.show_board_with_code),
    path('validate_code/<code>',views.validate_code),
    path('get_user_name/<pk>',views.get_user_name),
    path('leaderboard/<board_pk>',views.leaderboard),
    path('share_code',views.share_code),
    path('marchMadness/<board_number>', views.addToMarchMadnessTable),
    path('validate_creator/<token>/<board_number>', views.validate_creator)




]