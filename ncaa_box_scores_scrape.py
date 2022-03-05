from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import re
import time,datetime
from collections import defaultdict


#need to change input date with scraped dates
game_date = datetime.date(2021,3,21)


def cbb_scores(game_date):
'''
Pulls the NCAA MM ending game scores from Basketball Sports Reference
Inputs: Python Date variable to pull game scores from March Madness tournament
Outputs: List of dictionaries with game scores; end_score key holds pairing of ending scores (winner,loser)

'''
	opts = Options()
	opts.add_argument('--headless')
	browser = webdriver.Chrome(options=opts)
	browser.get(f'https://www.sports-reference.com/cbb/boxscores/index.cgi?month={str(game_date.month)}&day={str(game_date.day)}&year={str(game_date.year)}')

	games = browser.find_elements_by_xpath('//table[@class="teams"]')



	gm_list = []
	for i,game in enumerate(games):
    		if 'NCAA' in (game.find_element_by_class_name('desc').text):
			gm = {}
			gm['id'] = i
			gm['date'] = day
			gm['round'] = game.find_element_by_class_name('desc').text.split('-')[-1].strip()
			l = game.find_element_by_class_name('loser').text.strip()
			w = game.find_element_by_class_name('winner').text.strip()
			gm['lteam'] = re.sub('[\d]','',re.sub('[(]\d+[)]','',re.sub('OT|Final','',l))).strip().replace("-",' ')
			gm['lscore'] = int(re.sub('[^\d]','',re.sub('[(]\d+[)]','',re.sub('OT|Final','',l))))
			gm['wteam'] = re.sub('[\d]','',re.sub('[(]\d+[)]','',re.sub('OT|Final','',w))).strip().replace("-",' ')
			gm['wscore'] = int(re.sub('[^\d]','',re.sub('[(]\d+[)]','',re.sub('OT|Final','',w))))
			gm['end_score'] = (str(gm['wscore'])[-1],str(gm['lscore'])[-1])
			gm_list.append(gm)
	return gm_list

