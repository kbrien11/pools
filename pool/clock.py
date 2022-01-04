from apscheduler.schedulers.blocking import BlockingScheduler
from .views import addMoneyToWinners

sched = BlockingScheduler()



@sched.scheduled_job('cron',day_of_week ='tue',hour=19)
def scheduled_job():
    print('This job is run every weekday at 5pm.')
    addMoneyToWinners()

sched.start()
