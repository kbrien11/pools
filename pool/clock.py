from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from .views import addMoneyToWinners

sched = BackgroundScheduler()



@sched.scheduled_job(addMoneyToWinners,day_of_week ='tue',hour=19, minute=30)
def scheduled_job():
    print('This job is run every weekday at 5pm.')
   

sched.start()
