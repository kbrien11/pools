from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
import json
import re
import pandas as pd
import numpy as np
import time,datetime, math
from collections import defaultdict
import os

import environ

os.environ['DJANGO_SETTINGS_MODULE'] = 'pools.settings'



sched = BlockingScheduler()





@sched.scheduled_job( 'interval', minutes=2)
def scheduled_job():
    print('This job is run every weekday at 5pm.')


   

sched.start()
