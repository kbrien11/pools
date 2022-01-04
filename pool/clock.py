from apscheduler.schedulers.blocking import BlockingScheduler
from .views import addMoneyToWinners

sched = BlockingScheduler()



@sched.scheduled_job(addMoneyToWinners,'cron', day_of_week='mon-fri', hour=17)
def scheduled_job():
    print('This job is run every weekday at 5pm.')

sched.start()
