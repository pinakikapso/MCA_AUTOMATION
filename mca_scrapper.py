from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
import pandas as pd
import os
import time
import requests
from sqlalchemy import create_engine
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import *
from database.mongodb import Mongodb
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
import threading
from proxy.Proxy import GetProxy
from itertools import combinations 
from itertools import product  
from selenium.webdriver.support.ui import Select
import random
from webdriver_manager.chrome import ChromeDriverManager
with open('CINS.txt','r') as f:
    CINS=f.read().split('\n')
PATH=os.path.abspath('Driver')
URL='http://www.mca.gov.in/'
#PROXY_URL='https://free-proxy-list.net/'
PROXY_URL='http://proxy.link/list/get/f0560a60eb15710ba7bf875771e82090?geo=true'
PROXY_TXT='proxies.txt'
import concurrent.futures
md=Mongodb()
class Scrapper:
    def __init__(self,url,prox_obj=None):
        self.url=url
        self.webdriver=webdriver
        self.prox=prox_obj
        self.last_k=0
        self.last_d=0
        self.driver=None
    def use_proxy(self):
        while True:
            PROXY=random.choice(self.prox.getProxies())
            self.webdriver.DesiredCapabilities.CHROME['proxy'] = {
                "proxyType": "manual",
                "httpProxy": PROXY,
                "ftpProxy": PROXY,
                "sslProxy": PROXY
                }
            #fp.set_preference("general.useragent.override",agent)
            self.driver=self.webdriver.Chrome(ChromeDriverManager().install())
            try:
                self.driver.get(self.url)
                time.sleep(5)
                break
            except:
                pass
                self.driver.close()
    def get_data1(self,page):
        soup=BeautifulSoup(page,'html.parser')
        results=soup.find(id='results')
        if results is None:
            raise Exception('status 0')
    def get_data(self,page,cins):
        soup=BeautifulSoup(page,'html.parser')
        results=soup.find(id='results')
        if results is None:
            return None
        data_list=[]
        for row in  results.find_all('tr'):
            if len(row('td'))!=0:
                    data_list.append({'CIN':cins,'Document Name':row('td')[0].text.replace('\t','').replace('\n',''),
                    'Date of Filling':row('td')[1].text.replace('\t','').replace('\n','')})
        return data_list
    def get_values(self,page,i):
        soup=BeautifulSoup(page,'html.parser')
        d=soup.find(id=i)
        if d is None:
            return None
        data=[opt['value'] for opt in d.find_all('option')]
        return data[1:]

    
    def extract(self,cin):
        t=100000
        delay=4
        print(f'cin :{cin}')
        mca=WebDriverWait(self.driver, t).until(presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/nav/div/ul/li[5]/a')))
        view_doc=WebDriverWait(self.driver, t).until(presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/nav/div/ul/li[5]/div/div/div/ul[4]/li[1]/ul/li[2]/a')))
        time.sleep(delay)
        actions=ActionChains(self.driver)
        t1=time.time()
        actions.move_to_element(mca).move_to_element(view_doc).click().perform()
        time.sleep(delay)
        if (time.time()-t1)>10:
            self.driver.refresh()
        check_box=WebDriverWait(self.driver, t).until(element_to_be_clickable((By.ID,'cinChk')))
        check_box.click()
        time.sleep(delay)
        inp=WebDriverWait(self.driver, t).until(presence_of_element_located((By.ID,'cinFDetails')))
        inp.send_keys(cin)
        time.sleep(delay/2)
        submit1=WebDriverWait(self.driver, t).until(element_to_be_clickable((By.ID,'viewDocuments_0')))
        submit1.click()
        time.sleep(delay/2)
        status_page=self.driver.page_source
        self.get_data1(status_page)
        status=WebDriverWait(self.driver, t).until(element_to_be_clickable((By.XPATH,'/html/body/div[1]/div[6]/div[1]/section/form/table[3]/tbody/tr[2]/td[2]/a')))
        status.click()
        time.sleep(delay)
        doc_page=self.driver.page_source
        cats=self.get_values(doc_page,i="viewCategoryDetails_categoryName")
        dates=self.get_values(doc_page,i="viewCategoryDetails_finacialYear")
        if cats is None or dates is None:
            self.driver.refresh()
        for c in cats:
            cat_select=Select(WebDriverWait(self.driver, t).until(presence_of_element_located((By.ID,'viewCategoryDetails_categoryName'))))
            cat_select.select_by_value(c)
            time.sleep(delay)
            for d in dates[0:18]:
                year_select=Select(WebDriverWait(self.driver, t).until(presence_of_element_located((By.ID,"viewCategoryDetails_finacialYear"))))
                time.sleep(delay)
                year_select.select_by_value(d)
                try:
                    t2=time.time()
                    WebDriverWait(self.driver, 100000).until(element_to_be_clickable((By.ID,'viewCategoryDetails_0'))).click()
                    table_page=self.driver.page_source
                    data=self.get_data(table_page,cin)
                    if ((time.time()-t2)>50) or (data is None):
                        self.driver.refresh()
                    md._insert(data)
                except:
                    time.sleep(0.5)
                    WebDriverWait(self.driver, 100000).until(element_to_be_clickable((By.ID,'msgboxclose'))).click()
                    time.sleep(0.5)
                    if (time.time()-t2)>50:
                        self.driver.refresh()

        self.driver.close()
    def scrap(self,cin):
        if self.prox:
            self.use_proxy()
        else:
            self.driver=self.webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(self.url)
        self.driver.maximize_window()
        self.extract(cin)
def main():
    #prox=GetProxy(PROXY_URL)
    scrp=Scrapper(URL,None)
    n_cins=len(CINS)
    print(n_cins)
    i=46
    while i<=len(CINS):
        try:
            print('Total cins',i)
            scrp.scrap(CINS[i])
            i+=1
            print('Next')
        except Exception as e:
            if e.args[0]=='status 0':
                i+=1
                print(e.args[0])
                scrp.driver.close()
                time.sleep(0.5)
                scrp.scrap(CINS[i])
            else:
                print('Exception')
                scrp.driver.close()
                scrp.scrap(CINS[i])
if __name__ == "__main__":
    main()
       
