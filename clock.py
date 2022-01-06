from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'pools.settings'



sched = BlockingScheduler()





@sched.scheduled_job( 'interval', minutes=1)
def scheduled_job():
    print('This job is run every weekday at 5pm.')
 


sched.start()

