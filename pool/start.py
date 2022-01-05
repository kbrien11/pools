import schedule
import time

def job():
    print("hello keith ")

    schedule.every(1).minutes.at(":00").do(job)


while True:
    schedule.run_pending()
    time.sleep(1)
