from django.core.management.base import BaseCommand, CommandError

from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'pools.settings'

# class Command(BaseCommand):
#     help = 'Closes the specified poll for voting'



#     def handle(self, *args, **options):
#        print("running command")


# sched = BlockingScheduler()

# @sched.scheduled_job('interval', minutes=1)
def scheduled_job():
   print('This job is run every weekday at 5pm.')
#    addMoneyToWinners()
#    subprocess.call(('python manage.py keth'), shell = True, close_fds = True)

# sched.start()
