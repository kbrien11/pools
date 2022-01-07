from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'pools.settings'



sched = BlockingScheduler()


from .pool import *


@sched.scheduled_job( 'interval', minutes=2)
def scheduled_job():
    print('This job is run every weekday at 5pm.')


    
    views.addMoneyToWinners()

sched.start()
