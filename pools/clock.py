from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler



sched = BlockingScheduler()





@sched.scheduled_job( 'interval', minutes=2)
def scheduled_job():
    print('This job is run every weekday at 5pm.')


sched.start()
