from django.core.management.base import BaseCommand, CommandError
from ...views import addMoneyToWinners
from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import date,datetime


os.environ['DJANGO_SETTINGS_MODULE'] = 'pools.settings'

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'



    def handle(self, *args, **options):
       print("running command")


       sched = BlockingScheduler()

       @sched.scheduled_job( 'cron',day_of_week='mon-fri', hour=22, minute=30)
       def scheduled_job():
           print('This job is to run on jan 13th at 9:15.')
           addMoneyToWinners()
           subprocess.call(('python manage.py clock'), shell = True, close_fds = True)

       sched.start()
