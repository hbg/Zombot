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
                sub_sites = markov_values[kwargs.get("site")]
            except KeyError:
                print("Not visited by model")
                sub_sites = self.get_response(self, kwargs.get("site"))
            except urllib.error.HTTPError:
                print("Invalid URL")
                return self.layer()
            p = []
            e = []
            for pair in sub_sites:
                e.append(pair[0])
                p.append(pair[1])
            sample = np.random.choice(e, 1, p=p)[0]
            self.visit(sample)
            self.layer(site=sample)
        else:
            model = open("model.json").read()
            markov_values = json.loads(model)
            p = []
            e = []
            for pair in markov_values[list(markov_values.keys())[0]]:
                e.append(pair[0])
                p.append(pair[1])
            sample = np.random.choice(e, 1, p=p)[0]
            self.visit(sample)
            self.layer(site=sample)

    def train(self):
        self.current_url = browser.current_url
        while True:
            try:
                if browser.current_url != self.current_url:
                    results = self.get_response(self, self.current_url)
                    count = len(results)
                    for line in results:
                        if self.master.get(self.current_url):
                            if browser.current_url in results:
                                self.master[self.current_url].append(
                                    [line, (count - int(count / 2)) / (count * (count - 1))]) if line != browser.current_url else self.master[self.current_url].append((line, int(count / 2) / count))
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
