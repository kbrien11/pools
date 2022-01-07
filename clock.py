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





@sched.scheduled_job( 'interval', minutes=1)
def scheduled_job():
    print('This job is run every weekday at 5pm.')

    CHROME_DRIVER = os.environ.get("CHROME_DRIVER")


    '''loads headless invisible browser on your machine and opens CBS NFL scores page.
        Returns: a google chrome browser'''
    opts = Options()
    opts.add_argument('--headless')
    # s = Service(r"C:\Users\kbrie\Downloads\chromedriver_win32/chromedriver")
    web = webdriver.Chrome(options=opts,
                           executable_path=r"C:\Users\kbrie\Downloads\chromedriver_win32/chromedriver")  # can set executable path if needed here: executable_path='chromedriver'\
    web.get('https://www.cbssports.com/nfl/scoreboard/')
    tot_scores = web.find_elements_by_xpath('.//td[@class="total-score"]')
    if len(tot_scores) == 0:
        # most recent week of scores\
        web.find_element_by_id('ToggleContainer-buttons-button-1').click()
    gms = web.find_elements_by_xpath('//div[contains(@id,"game")]')
    '''Use open_link function return value to populate correct web browser instance for score data'''
    num_names = {}
    num_names[1] = "first"
    num_names[2] = "second"
    num_names[3] = "third"
    num_names[4] = "fourth"
    num_names[5] = "OT"
    num_names[6] = "2OT"
    num_names[7] = "3OT"
    num_names[8] = "4OT"
    num_names[9] = "5OT"
    num_names[10] = "6OT"
    gm_list = []
    for idx, game in enumerate(gms):
        gm = defaultdict()
        gm['id'] = idx
        run_tot = 0
        run_tot2 = 0
        totals = game.find_elements_by_xpath('.//td[@class="total-score"]')
        if len(totals) == 0:
            gm['total_away'] = 0
            gm['total_home'] = 0
        else:
            gm['total_away'] = totals[0].text
            gm['total_home'] = totals[1].text
        names = game.find_elements_by_xpath('.//a[contains(@class,"team")]')
        gm['team_away'] = names[0].text
        gm['team_home'] = names[1].text

        scores = game.find_elements_by_xpath('.//td[@class="scores"]')
        if len(scores) > 0:
            for i, score in enumerate(scores):
                if score.text == '-':
                    gm['status'] = 'in_progress'
                    score_data = 0
                else:
                    gm['status'] = 'completed'
                    score_data = int(score.text)
                if len(scores) == 8:
                    if i <= 3:
                        key = num_names[i + 1]
                        gm["a" + str(i + 1)] = score_data
                        run_tot += int(score_data)
                        gm[key] = [str(run_tot)[-1]]
                    else:
                        key = num_names[i - 3]
                        gm["h" + str(i - 3)] = score_data
                        run_tot2 += int(score_data)
                        gm[key].append(str(run_tot2)[-1])
                else:
                    if i <= 4:
                        key = num_names[i + 1]
                        gm["a" + str(i + 1)] = score_data
                        run_tot += int(score_data)
                        gm[key] = [str(run_tot)[-1]]
                    else:
                        key = num_names[i - 4]
                        gm["h" + str(i - 4)] = score_data
                        run_tot2 += int(score_data)
                        gm[key].append(str(run_tot2)[-1])

            gm_list.append(gm)
    print(gm_list)
    return gm_list


sched.start()
