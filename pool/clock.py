from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler



sched = BlockingScheduler()

def do():
    print("printing this scheduler')



@sched.scheduled_job(do, 'interval', minutes=2)
def scheduled_job():
    print('This job is run every weekday at 5pm.')


sched.start()


