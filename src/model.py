import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import json
import time
DRIVER = 'C:\Python27\selenium\webdriver\chromedriver.exe'
HEADER = {'User-Agent': 'Mozilla/5.0'}
browser = webdriver.Chrome(DRIVER)
# URL = "https://api.hackertarget.com/pagelinks/?q="


class Model(object):
    def __init__(self):
        self.master = {}
        self.current_url = ""
    def get_response(self, site):
        links = []
        req = Request(site, headers=HEADER)
        resp = urlopen(req)
        html = BeautifulSoup(resp)
        for href in html.find_all('a', href=True):
            if href['href'][0:1] == '/':
                links.append(browser.current_url + href['href'])
            else:
                links.append(href['href'])
        return links

    def emulate(self):
        path = []
        model = open("model.json").read()
        markov_values = json.loads(model)
        for key, value in markov_values.items():
            p = []
            e = []
            for pair in value:
                e.append(pair[0])
                p.append(pair[1])
            sample = np.random.choice(e, 1, p)[0]
            path.append(sample)
        for website in path:
            try:
                browser.get(website)
                time.sleep(1)
            except:
                print("URL {} doesn't work".format(website))



    def train(self):
        self.current_url = browser.current_url
        while True:
            try:
                if browser.current_url != self.current_url:
                    results = self.get_response(self.current_url)
                    count = len(results)
                    for line in results:
                        if self.master.get(self.current_url):
                            if browser.current_url in results:
                                self.master[self.current_url].append((line, (count-int(count/2))/(count*(count-1)))) if line != browser.current_url else self.master[self.current_url].append((line, int(count/2)/count))
                            else:
                                self.master[self.current_url].append((line, 1/count))
                        else:
                            if browser.current_url in results:
                                self.master[self.current_url] = [(line, (count-int(count/2))/(count*(count-1)))] if line != browser.current_url else [(line, int(count/2)/count)]
                            else:
                                self.master[self.current_url] = [(line, 1/len(results))]
                    with open('model.json', 'w') as f:
                        json.dump(self.master, f)
                    self.current_url = browser.current_url
            except KeyboardInterrupt:
                break
