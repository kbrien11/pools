from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler



sched = BlockingScheduler()



@sched.scheduled_job(day_of_week ='mon-fri',hour=10)
def scheduled_job():
    print('This job is run every weekday at 5pm.')


sched.start()


