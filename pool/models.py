from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

User._meta.get_field('username')._unique = True
User._meta.get_field('email')._unique = True


# class Boxes(models.Model):
#     user_pk = models.ForeignKey(User, on_delete=models.CASCADE())
#     pair = models.CharField(max_length=5,blank=False)
#     board_number = models.ForeignKey(Board, on_delete=models.CASCADE(()))



class Board(models.Model):
    code = models.IntegerField(null=False,default=0)
    type = models.CharField(default="", max_length=10)
    name = models.CharField(default="" , max_length=20,unique=True,null=False)

class Box(models.Model):
   user_pk = models.ForeignKey(User, on_delete=models.CASCADE,null=True , default="")
   pair = models.CharField(max_length=10,blank=False)
   board_number = models.ForeignKey(Board, on_delete=models.CASCADE)
   username = models.CharField(default="",max_length=42)
   balance = models.FloatField(default=0)
   hit = models.BooleanField(default=False)
   count = models.IntegerField(default=0)


class NFL(models.Model):
    one = models.FloatField(blank= False)
    two = models.FloatField(blank=False)
    three = models.FloatField(blank=False)
    four = models.FloatField(blank=False)
    board_number = models.ForeignKey(Board, on_delete=models.CASCADE)
    box_price = models.FloatField(blank=False, default=0)

class MarchMadness(models.Model):
    first_round = models.FloatField(blank=False,default=0)
    second_round = models.FloatField(blank=False, default=0)
    sweet_sixteen = models.FloatField(blank=False, default=0)
    elite_eight = models.FloatField(blank=False, default=0)
    final_four = models.FloatField(blank=False, default=0)
    championship = models.FloatField(blank=False, default=0)
    board_number = models.ForeignKey(Board, on_delete=models.CASCADE)
    box_price = models.FloatField(blank=False, default=0)

class Winnings(models.Model):
    user_pk = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default="")
    balance = models.FloatField(default=0)
    username = models.CharField(default="", max_length=42)
    board_pk = models.CharField(default="", max_length=42)

class Admin(models.Model):
    user_pk = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default="")
    board_number = models.ForeignKey(Board, on_delete=models.CASCADE)
    creator = models.BooleanField(default=False)


class GeneratedNumbers(models.Model):
    winning =  ArrayField(models.IntegerField(blank=True), default=list)
    losing =  ArrayField(models.IntegerField(blank=True), default=list)
    board_pk = models.CharField(default="", max_length=20)

    

class ScrapeData(models.Model):
    home_team = models.CharField(max_length=20,blank=False)
    away_team = models.CharField(max_length=20, blank=False)

