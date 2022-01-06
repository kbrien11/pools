from django.core.management.base import BaseCommand, CommandError
from ...views import addMoneyToWinners
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'pools.settings'

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'



    def handle(self, *args, **options):
       print("running command")


       sched = BackgroundScheduler()

       @sched.scheduled_job('interval', minutes=2)
       def scheduled_job():
           print('This job is run every weekday at 5pm.')
           addMoneyToWinners()

       sched.start()
