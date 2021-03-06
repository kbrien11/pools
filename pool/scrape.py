
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
import json
import re
import pandas as pd
import numpy as np
from .models import ScrapeData
import time,datetime, math
from collections import defaultdict
import os

import environ


CHROME_DRIVER = os.environ.get("CHROME_DRIVER")

def open_link():
    '''loads headless invisible browser on your machine and opens CBS NFL scores page.
        Returns: a google chrome browser'''
    opts = Options()
    opts.add_argument('--headless')
    # s = Service(r"C:\Users\kbrie\Downloads\chromedriver_win32/chromedriver")
    web = webdriver.Chrome(options=opts,executable_path=CHROME_DRIVER) #can set executable path if needed here: executable_path='chromedriver'\
    web.get('https://www.cbssports.com/nfl/scoreboard/')
    tot_scores = web.find_elements_by_xpath('.//td[@class="total-score"]')
    if len(tot_scores)==0:
        #most recent week of scores\
        web.find_element_by_id('ToggleContainer-buttons-button-1').click()
    return web


def pull_scores(web):
    gms = web.find_elements_by_xpath('//div[contains(@id, "game") and not(contains(@id,"pregame"))]')
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
    m = {}
    for idx,game in enumerate(gms):
        gm = defaultdict()
        print(gm)
        gm['id'] = idx
        run_tot = 0
        run_tot2 = 0
        totals = game.find_elements_by_xpath('.//td[@class="total-score"]')
        if len(totals)==0:
            gm['total_away'] = 0
            gm['total_home'] = 0
        else:
            gm['total_away'] = totals[0].text
            gm['total_home'] = totals[1].text
        names = game.find_elements_by_xpath('.//a[contains(@class,"team")]')
        if names[0].text in gm.values() or names[1].text in gm.values():
            print("has already been scraped")
            continue
        else:
            gm['team_away'] = names[0].text
            gm['team_home'] = names[1].text
            scraped_model = ScrapeData.objects.filter(home_team =names[1].text ,away_team = names[0].text).first()
            if scraped_model is not None:
                print("already been scapred")
                pass
            else:
                new_scrape_model = ScrapeData(home_team =names[1].text ,away_team = names[0].text)
                new_scrape_model.save()
                scores = game.find_elements_by_xpath('.//td[@class="scores"]')
                if len(scores)>0:
                    for i, score in enumerate(scores):
                        if score.text == '-':
                            gm['status'] = 'in_progress'
                            score_data = 0
                        else:
                            gm['status'] = 'completed'
                            score_data = int(score.text)

                        if len(scores)==8:
                            if i <=3:
                                key = num_names[i+1]
                                gm["a"+str(i+1)] = score_data
                                run_tot += int(score_data)
                                gm[key] = [str(run_tot)[-1]]
                            else:
                                key = num_names[i-3]
                                gm["h"+str(i-3)] = score_data
                                run_tot2 += int(score_data)
                                gm[key].append(str(run_tot2)[-1])
                        else:
                            if i<=4:
                                key = num_names[i+1]
                                gm["a"+str(i+1)] = score_data
                                run_tot += int(score_data)
                                gm[key] = [str(run_tot)[-1]]
                            else:
                                key = num_names[i-4]
                                gm["h"+str(i-4)] = score_data
                                run_tot2 += int(score_data)
                                gm[key].append(str(run_tot2)[-1])

                    print(m)
                    gm_list.append(gm)
    return gm_list
