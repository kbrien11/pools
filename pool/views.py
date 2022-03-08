from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password,make_password
from rest_framework.views import Response
from .models import Box,Board
from rest_framework.decorators import action,api_view
from .models import Board,Box,NFL,Winnings,MarchMadness,Admin,GeneratedNumbers,MarchMadnessDates
from rest_framework import viewsets,generics
from django.contrib.auth import authenticate
from .marchMadnessScraper import open_mm_link
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
from mailjet_rest import Client
import os
import environ
from .serializers import BoardSerializer,UserSerializer,BoxSerialiazer,NFLSerializer,WinningsSerializer,MarchMadnessSerializer,AdminSerializer,GeneratedNumbersSerializer,,MarchMadnessDatesSerializer

api_key = os.environ.get("API_KEY")
api_secret = os.environ.get("API_SECRET")

print(api_key,api_secret)

mailjet = Client(auth=(api_key, api_secret), version='v3.1')







@api_view(['POST'])
def createUser(request):
        password = request.data.get("password")
        email = request.data.get("email")
        first_name = request.data.get("first_name")
        serializer = UserSerializer(data=request.data)
        print(password)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.filter(username=serializer.data['username']).first()
            token = Token.objects.get(user=user)
            print(token)
            data = {
                'Messages': [
                    {
                        "From": {
                            "Email": "kbrien11@gmail.com",
                            "Name": "Keith"
                        },
                        "To": [
                            {
                                "Email": email,
                                "Name": first_name
                            }
                        ],
                        "Subject": "Thank you for registering",
                        "TextPart": "My first Mailjet email",
                        "HTMLPart": "<h3> Hi, {} thank you for signing up. Feel free to create a league or join an existing one. Goodluck on your boxes".format(str(first_name))

                    }
                ]
            }
            result = mailjet.send.create(data=data)
            print(result.json)
            return Response({"data":serializer.data, "token":token.key})
        else:
            return Response({"error":"errro"})


@api_view(['GET'])
def getBoardFromUser(request,token):
    boxes_list = []
    codes = []
    names = []
    user = Token.objects.get(key = token).user
    boxes  = Box.objects.filter(username=user).all()
    box_ser = BoxSerialiazer(boxes,many=True)
    for board_id in box_ser.data:
        if board_id['board_number'] in boxes_list:
            pass
        else:
            boxes_list.append(board_id['board_number'])

    for v in boxes_list:
        boards = Board.objects.filter(id = v).first()
        board_ser = BoardSerializer(boards,many=False)
        name = board_ser.data['name']
        code = board_ser.data['code']
        if len(name) >0:
            codes.append((name))
        else:
            codes.append((code))

    return Response({"codes":codes,"names":names})

@api_view(['POST'])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    user_obj = User.objects.filter(email__iexact=email).first()
    ser = UserSerializer(user_obj, many=False)
    print(user_obj)
    if user_obj:
        validate_password = check_password(password, ser.data['password'])
        print(validate_password, password)
        if validate_password:
            token = Token.objects.get(user=user_obj)
            print(token.key)
            return Response({'token': token.key})
        else:
            print("error logging in")
            return Response({"passwordError": "invalid password"})
    else:
        print("email is wrong")
        return Response({"EmailError": "invalid email"})




def valid_board_name_validator(x):
    if x.isalnum():
        print(x)
        return True
    else:
        return False


@api_view(['POST'])
def create_board(request,token):
    type = request.data.get("type")
    customize = request.data.get("customize")
    price = request.data.get("price")
    print(customize)
    board_name = request.data.get("name")
    if not valid_board_name_validator(board_name):
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        user = Token.objects.get(key=token).user
        data = UserSerializer(user, many=False)
        print(data.data['email'])
        generate_code = random.randint(100,10000)
        board = Board(code = generate_code,type=type,name=board_name,box_price=price)
        print(board.id)
        print('ceating board')
        winners_list = []
        losers_list = []
        total_pairs = []
        if board:
            if type == "football":
                print("football")
                price = int(request.data.get("price"))
                total_price = price*100

                four = int(request.data.get("four"))
                three = int(request.data.get("three"))
                two = int(request.data.get("two"))
                one = int(request.data.get("one"))
                four_decimail = four/100
                three_decimail = three / 100
                two_decimail = two / 100
                one_decimail = one / 100
                print(total_price)
                NFL_table = NFL(four=total_price*four_decimail, three=total_price*three_decimail, two=total_price*two_decimail , one= total_price*one_decimail, board_number=board,box_price=price)
                if NFL_table.one >=0 and NFL_table.two >=0 and NFL_table.three >=0 and NFL_table.four >=0:
                    print("inserting into money table")
                    board.save()
                    NFL_table.save()

                else:
                    print("not adding to board table")
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            elif type == "basketball":
                print("basketball")
                if customize == True:
                    first_round = int(request.data.get("first_round"))
                    second_round = int(request.data.get("second_round"))
                    sweet_sixteen = int(request.data.get("sweet_sixteen"))
                    elite_eight = int(request.data.get("elite_eight"))
                    final_four = int(request.data.get("final_four"))
                    price = int(request.data.get("price"))
                    championship = int(request.data.get("championship"))
                    march_madness = MarchMadness(first_round=first_round, second_round=second_round,
                                                 sweet_sixteen=sweet_sixteen,
                                                 elite_eight=elite_eight, final_four=final_four, championship=championship,
                                                 board_number=board,price=price)
                    if march_madness.first_round >= 0 and march_madness.second_round >= 0 and march_madness.sweet_sixteen >= 0 and march_madness.elite_eight >= 0 and march_madness.final_four >= 0 and march_madness.championship >= 0:
                        board.save()
                        march_madness.save()

                    else:
                        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    price = int(request.data.get("price"))
                    march_madness = MarchMadness(first_round=price *.5, second_round=price *1,
                                                 sweet_sixteen=price *2,
                                                 elite_eight=price*4, final_four=price*8, championship=price*20,
                                                 board_number=board, box_price=price)

                    if march_madness.first_round >= 0 and march_madness.second_round >= 0 and march_madness.sweet_sixteen >= 0 and march_madness.elite_eight >= 0 and march_madness.final_four >= 0 and march_madness.championship >= 0:
                        board.save()
                        march_madness.save()

                    else:
                        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            print(board)
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

            data = {
                'Messages': [
                    {
                        "From": {
                            "Email": "kbrien11@gmail.com",
                            "Name": "Keith"
                        },
                        "To": [
                            {
                                "Email": data.data['email'],
                                "Name": data.data['first_name']
                            }
                        ],
                        "Subject": "Thank you for Creating a new league",
                        "TextPart": "My first Mailjet email",
                        "HTMLPart": "<h3> Hi {}, thank you for creating a new board. Feel free to share this code --- {}--- and or link ---https://poolboxes.netlify.app/play--- with your friends.Goodluck on your boxes".format( str(data.data['first_name']),
                            str(board.code))

                    }
                ]
            }
            result = mailjet.send.create(data=data)
            print(result.json)
            new_Numbers = GeneratedNumbers(winning=winners_list,losing=losers_list,board_pk=board.id)
            new_Numbers.save()
            new_Numbers.winning
            return Response({"pairs":total_pairs,"board_nuber":board.id,"winningNumbers":new_Numbers.winning,"losingNumbers":new_Numbers.losing,"code":board.code})
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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
                    serializer.validated_data['first_name'] = data.data['first_name']

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
        numbers = GeneratedNumbers.objects.filter(board_pk=board_number).first()
        numbers_ser = GeneratedNumbersSerializer(numbers, many=False)
        return Response({"board":serializer.data,"winning":numbers.winning,"losing":numbers.losing})

@api_view(['GET'])
def game_in_progress(request,board_number):
    boxes = Box.objects.filter(board_number = board_number).all()
    for box in boxes:
        if box.username == "":
            return Response({"data":True})
        else:
            pass
    return Response({"data":False})

@api_view(['GET'])
def show_board_with_code(request,code):
    board_id = Board.objects.filter(code = code).first()
    if board_id:
        seriazlier = BoardSerializer(board_id,many = False)
        board_type = seriazlier.data['type']
        board_number = seriazlier.data['id']
        if board_number:
            numbers = GeneratedNumbers.objects.filter(board_pk=board_number).first()

            numbers_ser = GeneratedNumbersSerializer(numbers,many=False)
            print(numbers.winning)
            board_data = Box.objects.filter(board_number=board_number).order_by('id')
            serializer = BoxSerialiazer(board_data, many=True)
            return Response({"board": serializer.data,"board_nuber":board_number,"type":board_type,"winning":numbers.winning,"losing":numbers.losing})
    else:
        return Response({"error":"error"})

@api_view(['GET'])
def show_board_with_name(request,name):
    board_id = Board.objects.filter(name = name).first()
    if board_id:
        seriazlier = BoardSerializer(board_id,many = False)
        board_type = seriazlier.data['type']
        board_number = seriazlier.data['id']
        if board_number:
            numbers = GeneratedNumbers.objects.filter(board_pk=board_number).first()
            numbers_ser = GeneratedNumbersSerializer(numbers,many=False)
            board_data = Box.objects.filter(board_number=board_number).order_by('id')
            serializer = BoxSerialiazer(board_data, many=True)
            return Response({"board": serializer.data,"board_nuber":board_number,"type":board_type,"winning":numbers.winning,"losing":numbers.losing})
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
def validate_name(request,name):

    board_id = Board.objects.filter(name=name).first()
    seriazlier = BoardSerializer(board_id, many=False)
    board_number = seriazlier.data['code']
    if board_number:
        return Response({"code":name,"board":seriazlier.data['id']})
    else:
        return Response({"error":"wrong name"})

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



@api_view(['GET'])
def price_per_box(request,board_number):
    board = Board.objects.filter(id = board_number).first()
    seriazlier = BoardSerializer(board,many = False)
    print(seriazlier.data)
    price = seriazlier.data['box_price']
    print(price)
    if price:
        return Response({"price":price})
    else:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                    print(i)
                    if "OT" in i:
                        print(i["OT"])
                        print(type(i["OT"]))
                        winning_pair["four"] = tuple(i["OT"])
                        winning_pair["one"] = tuple(i['first'])
                        winning_pair["two"] = tuple(i["second"])
                        winning_pair["three"] = tuple(i["third"])
                    elif "2OT" in i:
                        winning_pair["one"] = tuple(i['first'])
                        winning_pair["two"] = tuple(i["second"])
                        winning_pair["three"] = tuple(i["third"])
                        winning_pair["four"] = tuple(i["2OT"])
                    else:
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
                                    print(k, v, box['pair'], box['id'],box_update.hit,box['username'])
                                    add_money_to_user = Winnings.objects.filter(user_pk=box['user_pk'],board_pk =box['board_number']).first()
                                    if NFL_ser.data[k] is not None:
                                        if add_money_to_user:
                                            add_money_to_user.balance += NFL_ser.data[k]
                                            add_money_to_user.save(update_fields=['balance'])
                                            user = User.objects.filter(pk=box['user_pk']).first()
                                            print(user)
                                        else:
                                            user_obj = User.objects.filter(pk = box['user_pk']).first()
                                            winner = Winnings(user_pk =  user_obj,balance = NFL_ser.data[k],username=box['username'],board_pk=str(box['board_number']),first_name=box['first_name'])
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


def addMoneyToWinnersForMarchMadness():
    game_dates_list = MarchMadnessDates.objects.all()
    dates_ser = MarchMadnessDatesSerializer(game_dates_list,many=True)
    for i in dates_ser.data:
        print(i)
        if i['visited'] ==True :
            print("{} has already been visited".format(i['date']))
            continue
        else:
            winning_pair = {}
            scores = open_mm_link(i['date'])
            count = 0
            scores_pairs = []
            date_to_update = MarchMadnessDates.objects.filter(id=i['id']).first()
            date_to_update.visited = True
            date_to_update.save(update_fields=['visited'])
            boards = Board.objects.filter(type='basketball').all()
            board_ser = BoardSerializer(boards,many=True)
            if board_ser:
                for pk in board_ser.data:
                    monies = MarchMadness.objects.filter(board_number = pk['id']).first()
                    MM_ser = MarchMadnessSerializer(monies,many=False)
                    boxes = Box.objects.filter(board_number = pk['id']).all()
                    box_data_ser = BoxSerialiazer(boxes,many=True)
                    if box_data_ser:
                        if scores is not None:
                            for i in scores:
                                if i['round'] == 'First Round':
                                  winning_pair["first_round"] = tuple(i['round'])

                                elif i['round'] == 'Second Round':
                                   winning_pair["second_round"] = tuple(i["round"])

                                elif i['round'] == 'Regional Semifinal':
                                    winning_pair["sweet_sixteen"] = tuple(i["round"])

                                elif i['round'] == 'Regional Final':
                                   winning_pair["elite_eight"] = tuple(i["round"])

                                elif i['round'] == 'National Semifinal':
                                   winning_pair["final_four"] = tuple(i["round"])

                                else:
                                   winning_pair["championship"] = tuple(i["round"])



                                for box in box_data_ser.data:
                                    for k,v in winning_pair.items():
                                     if box['pair'] == str(i['end_score']):
                                         count +=1
                                         print(i['end_score'])
                                         print(box['pair'],'match',count)
                                         box_update = Box.objects.filter(board_number = pk['id'],id=box['id']).first()
                                         if box_update.user_pk is not None:
                                            box_update.hit = True
                                            box_update.count +=1
                                            box_update.save(update_fields=['hit','count'])
                                            print(winning_pair[k], box['pair'], box['id'],box_update.hit)
                                            add_money_to_user = Winnings.objects.filter(user_pk=box['user_pk'],board_pk =box['board_number']).first()
                                            if MM_ser.data[k] is not None:
                                                if add_money_to_user:
                                                    add_money_to_user.balance += MM_ser.data[k]
                                                    add_money_to_user.save(update_fields=['balance'])
                                                    user = User.objects.filter(pk=box['user_pk']).first()
                                                    print(user)
                                                else:
                                                    user_obj = User.objects.filter(pk = box['user_pk']).first()
                                                    winner = Winnings(user_pk =  user_obj,balance = MM_ser.data[k],username=box['username'],board_pk=str(box['board_number']),first_name=box['first_name'])
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
                        else:
                            print('scores are none')

    print("all board have been scraped ad updated")
    return

@api_view(['POST'])
def insertDatesForMarchMadness(request):
    date = request.data.get('date')
    new_date = MarchMadnessDates(date = date)
    if new_date:
        new_date.save()
        return Response({"date":new_date.date})
    else:
        print("error adding {]".format(date))


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


def get_money_owed(request,boardPk):
    output = {}
    board = Board.objects.filter(id=boardPk).first()
    board_ser = BoardSerializer(board,many=False)
    amount = board_ser.data['box_price']
    boxes = Box.objects.filter(board_number = boardPk).all()
    boxes_ser = BoxSerialiazer(boxes,many = True)
    if boxes_ser:
        for i in boxes_ser.data:
            if i['username'] in output:
                output[i['username']] += int(amount)
            else:
                output[i['username']] = int(amount)


        return Response({"data":output})
    else:
        return Response({"error":"error"})

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


