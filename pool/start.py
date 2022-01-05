from .serializers import BoardSerializer,UserSerializer,BoxSerialiazer,NFLSerializer,WinningsSerializer,MarchMadnessSerializer,AdminSerializer
from .models import Board,Box,NFL,Winnings,MarchMadness,Admin
from .scrape import open_link,pull_scores
from django.contrib.auth.models import User

def addMoneyToWinners():
    print("starting scaper in schedule")
    winning_pair = {}
    openLink = open_link()
    scores = pull_scores(openLink)


    boards = Board.objects.all()
    board_ser = BoardSerializer(boards,many=True)
    if board_ser:
        for pk in board_ser.data:
            monies = NFL.objects.filter(board_number = pk['id']).first()
            NFL_ser = NFLSerializer(monies,many=False)
            boxes = Box.objects.filter(board_number = pk['id']).all()
            box_data_ser = BoxSerialiazer(boxes,many=True)
            if box_data_ser:
                for i in scores:
                    winning_pair["one"] = tuple(i['first'])
                    winning_pair["two"] = tuple(i["second"])
                    winning_pair["three"] = tuple(i["third"])
                    winning_pair["four"] = tuple(i["fourth"])
                    for box in box_data_ser.data:
                        for k, v in winning_pair.items():
                            if box['pair'] ==str(v):
                                box_update = Box.objects.filter(board_number = pk['id'],id=box['id']).first()
                                box_update.hit = True
                                box_update.count +=1
                                box_update.save(update_fields=['hit','count'])
                                print(k, v, box['pair'], box['id'],box_update.hit)
                                add_money_to_user = Winnings.objects.filter(user_pk=box['user_pk'],board_pk =box['board_number']).first()
                                if add_money_to_user:
                                    add_money_to_user.balance += NFL_ser.data[k]
                                    add_money_to_user.save(update_fields=['balance'])
                                    user = User.objects.filter(pk=box['user_pk']).first()
                                    print(user)
                                else:
                                    user_obj = User.objects.filter(pk = box['user_pk']).first()
                                    winner = Winnings(user_pk =  user_obj,balance = NFL_ser.data[k],username=box['username'],board_pk=str(box['board_number']))
                                    winner.save()

                            #        /SEND EMAIL TO NOTIFY USER THEY WON
                            else:
                                continue


        return  
