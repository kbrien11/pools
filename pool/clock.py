from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from .views import addMoneyToWinners

sched = BlockingScheduler()



@sched.scheduled_job(addMoneyToWinners,day_of_week ='wed',hour=11)
def scheduled_job():
    print('This job is run every weekday at 5pm.')


sched.start()


