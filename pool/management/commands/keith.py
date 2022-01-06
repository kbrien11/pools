from django.core.management.base import BaseCommand, CommandError
from ...views import addMoneyToWinners

os.environ['DJANGO_SETTINGS_MODULE'] = 'pools.settings'

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'



    def handle(self, *args, **options):
       print("running command")


       def scheduled_job():
           print('This job is run every weekday at 5pm.')
           addMoneyToWinners()

       sched.start()