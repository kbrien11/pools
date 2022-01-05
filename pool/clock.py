

from .views import addMoneyToWinners

def scheduled_job():
    print('This job is run every weekday at 5pm.')
    
    addMoneyToWinners()
   


