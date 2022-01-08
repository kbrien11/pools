from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password,make_password
from rest_framework.views import Response
from .models import Box,Board
from rest_framework.decorators import action,api_view
from .models import Board,Box,NFL,Winnings,MarchMadness,Admin
from rest_framework import viewsets,generics
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status
import random
from .scrape import open_link,pull_scores
from django.core.mail import send_mail
import schedule
import time
import threading
from datetime import date
from dateutil.parser import parse


from .serializers import BoardSerializer,UserSerializer,BoxSerialiazer,NFLSerializer,WinningsSerializer,MarchMadnessSerializer,AdminSerializer








@api_view(['POST'])
def createUser(request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.filter(username=serializer.data['username']).first()
            token = Token.objects.get(user=user)
            return Response({"data":serializer.data, "token":token.key})
        else:
            return Response({"error":"errro"})




@api_view(['GET'])
def getUser(request,username):
    user = User.objects.filter(username = username).first()
    print(user)
    serializer = UserSerializer(user,many = False)
    token = Token.objects.get(user=user)
    if serializer:
        return Response({"token": token.key})
    else:
        return Response({"error": "errro"})



@api_view(['POST'])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    user_obj = User.objects.filter(email=email).first()
    ser = UserSerializer(user_obj,many=False)
    print(ser['password'])
    if user_obj:
        validate_password  = check_password(password,ser.data['password'])
        print(validate_password , password)
        if validate_password:
            token = Token.objects.get(user=user_obj)
            print(token.key)
            return Response({'token':token.key})
        else:
            print("error logging in")
            return Response( {"error":"invalid password"})
    else:
        print("email is wrong")
        return Response({"error": "invalid email"})


@api_view(['POST'])
def create_board(request,token):
    type = request.data.get("type")
    user = Token.objects.get(key=token).user
    data = UserSerializer(user, many=False)
    print(data.data['email'])
    generate_code = random.randint(100,10000)
    board = Board(code = generate_code,type=type)
    print(board)
    winners_list = []
    losers_list = []
    total_pairs = []



    if board:
        board.save()
        new_admin = Admin(board_number = board,user_pk = user,creator=True)
        new_admin.save()
        win = [str(i) for i in range(10)]
        los = [str(i) for i in range(10)]
        random.shuffle(win)
        random.shuffle(los)

        print(data.data['email'])
        for j in win:
            winners_list.append(j)

        for i in los:
            losers_list.append(i)

        first = 0
        last = len(losers_list)

        while first < last:
            for num in winners_list:
                pair = num, losers_list[first]
                total_pairs.append(pair)
            first += 1

        for i in total_pairs:
            new_boxes = Box(pair = i,board_number = board)

            if new_boxes:
                new_boxes.save()
                print( Response(status=status.HTTP_202_ACCEPTED))
            else:
                print(Response(status = status.HTTP_400_BAD_REQUEST))

#         send_mail(
#             'league created',
#             'Hi {}, the code to join the leauge is {}'.format(
#                 user, board.code),
#             "kbrien11@gmail.com",
#             [data.data['email']],
#             fail_silently=False
#         )
        return Response({"pairs":total_pairs,"board_nuber":board.id,"winningNumbers":winners_list,"losingNumbers":losers_list,"code":board.code})

@api_view(['POST'])
def addToNFLTable(request,board_number):
    four = request.data.get("four")
    three = request.data.get("three")
    two = request.data.get("two")
    one = request.data.get("one")


    NFL_table = NFL(four=four, three=three, two=two, one=one, board_number=board_number)
    if NFL_table:
        print("inserting into money table")
        NFL_table.save()
    return Response(status=status.HTTP_202_ACCEPTED)

@api_view(['POST'])
def addToMarchMadnessTable(request,board_number):
    first_round = request.data.get("first_round")
    second_round = request.data.get("second_round")
    sweet_sixteen = request.data.get("sweet_sixteen")
    elite_eight = request.data.get("elite_eight")
    final_four = request.data.get("final_four")
    championship = request.data.get("championship")
    march_madness = MarchMadness(first_round = first_round,second_round=second_round,sweet_sixteen=sweet_sixteen,elite_eight=elite_eight,final_four = final_four,championship=championship,board_number=board_number)
    if march_madness:
        march_madness.save()
    return Response(status=status.HTTP_202_ACCEPTED)

@api_view(['POST'])
def addUserToBox(request,token,box_pk,board_number):

    user = Token.objects.get(key = token).user

    data = UserSerializer(user,many=False)
    print(data.data['username'])
    list_box_pk =list(box_pk.split(","))
    count = 0
    if user:
        for pk in list_box_pk:
            box_data = Box.objects.get(board_number=board_number,id=int(pk))

            serializer = BoxSerialiazer(instance=box_data,data=request.data,many=False,partial=True)
            if serializer.is_valid():

                if serializer.validated_data.get('user_pk') is None:
                    serializer.validated_data['user_pk'] =user
                    serializer.validated_data['username'] =data.data['username']


                    if serializer.validated_data['user_pk'] ==user:

                        serializer.save()
                        count +=1
                        print(serializer.validated_data)



                else:
                    print("box taken already")

#     send_mail(
#         'Chosen Boxes',
#         'Hi {} thank you for choosing {} box(es). Goodluck!'.format(data.data['first_name'],str(count)),
#         'kbrien11@gmail.com',
#         [data.data['email']],
#         fail_silently=False
#     )
    return Response({"data":serializer.data})



@api_view(['GET'])
def show_board(request,token,board_number):
    user = Token.objects.get(key=token).user
    if user:
        print(user, token)
        board_data = Box.objects.filter(board_number = board_number).order_by('id')
        serializer = BoxSerialiazer(board_data, many=True)
        return Response({"board":serializer.data})

@api_view(['GET'])
def show_board_with_code(request,code):
    board_id = Board.objects.filter(code = code).first()
    if board_id:
        seriazlier = BoardSerializer(board_id,many = False)
        board_type = seriazlier.data['type']
        board_number = seriazlier.data['id']
        if board_number:
            board_data = Box.objects.filter(board_number=board_number).order_by('id')
            serializer = BoxSerialiazer(board_data, many=True)
            return Response({"board": serializer.data,"board_nuber":board_number,"type":board_type})
    else:
        return Response({"error":"error"})
    
@api_view(['GET'])
def validate_code(request,code):

    board_id = Board.objects.filter(code=code).first()
    seriazlier = BoardSerializer(board_id, many=False)
    board_number = seriazlier.data['code']
    if board_number:
        return Response({"code":code,"board":seriazlier.data['id']})
    else:
        return Response({"error":"wrong code"})



@api_view(['GET'])
def verifyBox(request,token,box_id,board_number):
    user = Token.objects.filter(key=token).first()
    print(user)
    if user:
        username = Token.objects.get(key=token).user
        box_data = Box.objects.filter(board_number=board_number).filter(id =box_id).first()
        if box_data.user_pk is None:
            return Response({"user":username.username})
        else:
            return Response({"error":"error"})
    else:
        return Response({"error": "error"})

@api_view(['GET'])
def get_user_name(request,pk):
    user = User.objects.filter(id=pk).first()
    if user:
        query_set = UserSerializer(user,many=False)
        if query_set:
            print(query_set.data['username'])
            return Response({"user":query_set.data['username']})
        else:
            return Response({"error": "error"})






def addMoneyToWinners():
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
                                if box_update.user_pk is not None:
                                    box_update.hit = True
                                    box_update.count +=1
                                    box_update.save(update_fields=['hit','count'])
                                    print(k, v, box['pair'], box['id'],box_update.hit)
                                    add_money_to_user = Winnings.objects.filter(user_pk=box['user_pk'],board_pk =box['board_number']).first()
                                    if NFL_ser.data[k] is not None:
                                        if add_money_to_user:
                                            add_money_to_user.balance += NFL_ser.data[k]
                                            add_money_to_user.save(update_fields=['balance'])
                                            user = User.objects.filter(pk=box['user_pk']).first()
                                            print(user)
                                        else:
                                            user_obj = User.objects.filter(pk = box['user_pk']).first()
                                            winner = Winnings(user_pk =  user_obj,balance = NFL_ser.data[k],username=box['username'],board_pk=str(box['board_number']))
                                            winner.save()
                                    else:
                                        print("money board is empty")
                                        pass
                                else:
                                    print("board isnt fully filled out")
                                    pass

                                #        /SEND EMAIL TO NOTIFY USER THEY WON
                            else:
                              continue

        print("all board have been scraped ad updated")
        return




@api_view(['GET'])
def leaderboard(request,board_pk):
    output = []
    boxes = Winnings.objects.filter(board_pk = str(board_pk)).order_by('-balance').all()
    boxes_ser = WinningsSerializer(boxes,many=True)
    for box in boxes_ser.data:
        if box['balance'] >0:
            output.append(box)
    print(output)
    return Response({'data':output})

@api_view(['GET'])
def validate_creator(request,token,board_number):
    user_pk = Token.objects.filter(key=token).first()

    if user_pk is not None:
        print(user_pk.user_id)
        creator = Admin.objects.filter(board_number = board_number,user_pk = user_pk.user_id).first()
        if creator:
            serializer = AdminSerializer(creator,many=False)
            print(serializer.data)
            return Response({"data":serializer.data})
        else:
            return Response({"error":"error"})
    else:
        return Response({"error2": "error2"})

# @api_view(['POST'])
# def share_code(request):
#     board_pk = request.data.get('board_pk')
#     email = request.data.get('email')
#     print(board_pk,email)
#     board = Board.objects.filter(id=board_pk).first()
#     board_ser = BoardSerializer(board,many=False)
#     code = board_ser.data['code']
#     print(code)
#     user_to_email = User.objects.filter(email=email).first()
#     user_ser = UserSerializer(user_to_email,many=False)
#     if email:
#         if code:
#            if user_ser:
# #                 send_mail(
# #                     'Code to join my leage',
# #                     'Hi {}, the code to join the leage is {}'.format(
# #                         user_ser .data['username'], code),
# #                     "kbrien11@gmail.com",
# #                     [email],
# #                     fail_silently=False
# #                 )
#                 print("hi")
#            else:
#                  print("hi")
# #                 send_mail(
# #                     'Code to join my leage',
# #                     'Hi there, the code to join the league is {}'.format(
# #                          code),
# #                     "kbrien11@gmail.com",
# #                     [email],
# #                     fail_silently=False
# #                 )
#         else:
#             print("code error")
#     return Response({"data":code})


# def send_email_to_winners():
#     day = date.today()
#     check_date = ["2021-12-29","2021-12-30","2021-12-31","2021-12-28"]
#     if str(day) in check_date:
#         users = Winnings.objects.all()
#         ser = WinningsSerializer(users,many=True)
#         print("sending email script")
#         for i in ser.data:
#             email_user = User.objects.filter(username=i['username']).first()
#             email_ser = UserSerializer(email_user,many=False)
#             if email_ser.data['email']:
#                 print(email_ser.data['email'])
#                 send_mail(
#                     'Box hit',
#                     'Hi {}, your total balance/winning is {}'.format(
#                         email_ser.data['username'], i['balance']),
#                     "kbrien11@gmail.com",
#                     ["moneyman92m@yahoo.com"],
#                     # [email_ser.data['email']],
#                     fail_silently=False
#                 )
#             else:
#                 print(i['balance'],i['username'])
#     else:
#         print("wrong day")
#         return


def get_print():
    day = date.today()
    check_date = "2021-12-28"
    if str(day) == check_date:
        print(day)
    else:
        print("wrong day")

def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run




# Start the background thread
stop_run_continuously = run_continuously()

# schedule.every(5).seconds.until("2021-12-28 11:45").do(get_print)
# schedule.every(30).seconds.until("2021-12-28 11:55").do(send_email_to_winners)
schedule.every().tuesday.at("15:30").do(addMoneyToWinners)


# Do some other things...
time.sleep(1)


