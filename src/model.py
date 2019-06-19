import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import urllib
import json
import time
DRIVER = r'C:\Python27\selenium\webdriver\chromedriver.exe'
HEADER = {'User-Agent': 'Mozilla/5.0'}
browser = webdriver.Chrome(DRIVER)
# URL = "https://api.hackertarget.com/pagelinks/?q="

class Model(object):
    def __init__(self):
        self.master = {}
        self.current_url = ""

    @staticmethod
    def visit(sample):
        browser.get(sample)
        time.sleep(1)
        pass

    @staticmethod
    def get_response(self, site):
        links = []
        req = Request(site, headers=HEADER)
        resp = urlopen(req)
        html = BeautifulSoup(resp)
        for href in html.find_all('a', href=True):
            if href['href'][0:1] == '/':
                # Using slices is a bit weird, but it may come in handy
                links.append("https://github.com" + href['href'])
            elif href['href'][0:1] == '#':
                links.append(self.current_url + href['href'])
            else:
                links.append(href['href'])
        return links

    def emulate(self):
        self.layer()

    def layer(self, **kwargs):
        if kwargs.get("site"):
            model = open("model.json").read()
            markov_values = json.loads(model)
            try:
                sub_sites = markov_values[kwargs.get("site")].items()
                p = []
                e = []
                sum = 0
                for key, value in sub_sites:
                    e.append(key)
                    p.append(value)
                    sum+=value
                for i in range(0, len(p)):
                    p[i] /= sum
                sample = np.random.choice(e, 1, p=p)[0]
                self.visit(sample)
                self.layer(site=sample)
            except KeyError:
                print("Not visited by model")
                sub_sites = self.get_response(self, kwargs.get("site"))
                sample = np.random.choice(sub_sites, 1)[0]
                self.visit(sample)
                self.layer(site=sample)
            except urllib.error.HTTPError:
                print("Invalid URL")
                return self.layer()
            except Exception:
                return self.layer()
        else:
            model = open("model.json").read()
            markov_values = json.loads(model)
            p = []
            e = []
            sum = 0
            for key, value in markov_values[list(markov_values.keys())[0]].items():
                e.append(key)
                p.append(value)
                sum+=value
            for i in range(0, len(p)):
                p[i] /= sum
            sample = np.random.choice(e, 1, p=p)[0]
            self.visit(sample)
            self.layer(site=sample)

    def train(self):
        self.current_url = browser.current_url
        while True:
            try:
                if browser.current_url != self.current_url:
                    results = self.get_response(self, self.current_url)
                    for line in results:
                        if self.current_url not in self.master.keys():
                            self.master[self.current_url] = {}
                        if line not in self.master[self.current_url].keys():
                            self.master[self.current_url][line] = 1
                        if line == browser.current_url:
                            self.master[self.current_url][line] = self.master[self.current_url][line]+1
                    with open('model.json', 'w') as f:
                        json.dump(self.master, f, sort_keys=True, indent=4)
                    self.current_url = browser.current_url
            except KeyboardInterrupt:
                break
            
    def check(self, URL):
        urls = self.master[self.current_url]
        for i in range(0, len(urls)):
            if urls[i][0] == URL:
                index = i
                return i
        return True
