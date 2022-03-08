
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

from .models import ScrapeData
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


#need to change input date with scraped dates
# game_date = datetime.date(2021,3,19)
CHROME_DRIVER = os.environ.get("CHROME_DRIVER")

def open_mm_link(i):
            try:
                date = i.split(",")
                year = date[0]
                month = date[1]
                day = date[2]

                opts = Options()
                opts.add_argument('--headless')
                web = webdriver.Chrome(options=opts,executable_path=CHROME_DRIVER) #can set executable path if needed here: executable_path='chromedriver'\
                game_date = datetime.date(int(year),int(month),int(day))


                web.get(f'https://www.sports-reference.com/cbb/boxscores/index.cgi?month={str(game_date.month)}&day={str(game_date.day)}&year={str(game_date.year)}')
                games = web.find_elements_by_xpath('//table[@class="teams"]')

                gm_list = []
                for i, game in enumerate(games):
                     if 'NCAA' in (game.find_element_by_class_name('desc').text):
                        gm = {}
                        gm['id'] = i
                        gm['date'] = game_date
                        gm['round'] = game.find_element_by_class_name('desc').text.split('-')[-1].strip()
                        l = game.find_element_by_class_name('loser').text.strip()

                        if game.find_element_by_class_name('winner').text.strip() is not None:
                            w = game.find_element_by_class_name('winner').text.strip()
                            gm['lteam'] = re.sub('[\d]', '', re.sub('[(]\d+[)]', '', re.sub('OT|Final', '', l))).strip().replace("-", ' ')
                            gm['lscore'] = int(float(re.sub('[^\d]', '', re.sub('[(]\d+[)]', '', re.sub('OT|Final', '', l)))))

                            gm['wteam'] = re.sub('[\d]', '', re.sub('[(]\d+[)]', '', re.sub('OT|Final', '', w))).strip().replace("-", ' ')
                            gm['wscore'] = int(float(re.sub('[^\d]', '', re.sub('[(]\d+[)]', '', re.sub('OT|Final', '', w)))))
                            gm['end_score'] = (str(gm['wscore'])[-1], str(gm['lscore'])[-1])
                            gm_list.append(gm)
                        else:
                            print("error")
                            continue
            except NoSuchElementException:
                print("error")

                return gm_list
