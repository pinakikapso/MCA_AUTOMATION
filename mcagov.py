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
from webdriver_manager.chrome import ChromeDriverManager
import threading
from proxy.Proxy import GetProxy
with open('CINS.txt','r') as f:
    CINS=f.read().split('\n')
PATH=os.path.abspath('Driver')
URL='http://www.mca.gov.in/'
#PROXY_URL='https://free-proxy-list.net/'
PROXY_URL='http://proxy.link/list/get/f0560a60eb15710ba7bf875771e82090?geo=true'
PROXY_TXT='proxies.txt'
md=Mongodb()
class Scrapper:
    def __init__(self,url,prox_obj=None):
        self.url=url
        self.webdriver=webdriver
        self.prox=prox_obj
    def use_proxy(self):
        PROXY=self.prox.get_proxy()
        print(PROXY)
        profile=self.webdriver.FirefoxProfile()
        profile.set_preference('network.proxy_type',1)
        profile.set_preference('network.proxy.http',PROXY.split(':')[0])
        profile.set_preference('network.proxy.http_port',PROXY.split(':')[1])
        profile.update_preferences()
        self.driver=self.webdriver.Firefox(executable_path=PATH+r'\geckodriver.exe',firefox_profile=profile)
    def get_data(self,page,cins):
        soup=BeautifulSoup(page,'html.parser')
        results=soup.find(id='results')
        #print(results.find_all('tr'))
        data={'CIN':[],'Document Name':[],'Date of Filling':[]}
        for row in  results.find_all('tr'):
            if len(row('td'))!=0:
                if row('td')[0].text.replace('\t','').replace('\n','') not in data['Document Name']:
                    data['CIN'].append(cins)
                    data['Document Name'].append(row('td')[0].text.replace('\t','').replace('\n',''))
                    data['Date of Filling'].append(row('td')[1].text.replace('\t','').replace('\n',''))
                
        return data
    def get_values(self,page,i):
        soup=BeautifulSoup(page,'html.parser')
        d=soup.find(id=i)
        data=[opt['value'] for opt in d.find_all('option')]
        return data[1:]
    
    def scrap(self,cin):
        df=None
        t=20
        if self.prox:
            self.use_proxy()
        else:
            self.driver=self.webdriver.Firefox(executable_path=PATH+r'\geckodriver.exe')
        try:
            self.driver.get(self.url)
            self.driver.maximize_window()
        except:
             self.driver.refresh()
        #mca=self.driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/nav/div/ul/li[5]/a')
        mca=WebDriverWait(self.driver, t).until(presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/nav/div/ul/li[5]/a')))
        #view_doc=self.driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/nav/div/ul/li[5]/div/div/div/ul[4]/li[1]/ul/li[2]/a')
        #WebDriverWait(self.driver, 20).until(visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/nav/div/ul/li[5]/div/div/div/ul[4]/li[1]/ul/li[2]/a')))
        view_doc=self.driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/nav/div/ul/li[5]/div/div/div/ul[4]/li[1]/ul/li[2]/a')
        time.sleep(1)
        actions=ActionChains(self.driver)
        actions.move_to_element(mca).move_to_element(view_doc).click().perform()
        time.sleep(1)
        #check_box=WebDriverWait(self.driver, t).until(element_to_be_clickable((By.XPATH,'/html/body/div[1]/div[6]/div[1]/section/form/table[1]/tbody/tr[3]/td[1]/input[1]')))
        check_box=WebDriverWait(self.driver, t).until(element_to_be_clickable((By.ID,'cinChk')))
        time.sleep(1)
        check_box.click()
        #inp=self.driver.find_element_by_xpath('/html/body/div[1]/div[6]/div[1]/section/form/table[1]/tbody/tr[3]/td[2]/input')
        #inp=WebDriverWait(self.driver, t).until(visibility_of_element_located((By.XPATH,'/html/body/div[1]/div[6]/div[1]/section/form/table[1]/tbody/tr[3]/td[2]/input')))
        time.sleep(1)
        inp=WebDriverWait(self.driver, t).until(presence_of_element_located((By.ID,'cinFDetails')))
        time.sleep(1)
        inp.send_keys(cin)
        time.sleep(1)
        #submit1=self.driver.find_element_by_xpath('/html/body/div[1]/div[6]/div[1]/section/form/table[2]/tbody/tr/td[1]/input')
        submit1=WebDriverWait(self.driver, t).until(element_to_be_clickable((By.ID,'viewDocuments_0')))
        submit1.click()
        #status=self.driver.find_element_by_xpath('/html/body/div[1]/div[6]/div[1]/section/form/table[3]/tbody/tr[2]/td[2]/a')
        status=WebDriverWait(self.driver, t).until(element_to_be_clickable((By.XPATH,'/html/body/div[1]/div[6]/div[1]/section/form/table[3]/tbody/tr[2]/td[2]/a')))
        time.sleep(1)
        status.click()
        time.sleep(1)
        #doc_cat=self.driver.find_element_by_xpath('/html/body/div[1]/div[6]/div[1]/section/form[1]/table/tbody/tr[2]/td[2]/select')
        doc_cat=WebDriverWait(self.driver, t).until(presence_of_element_located((By.ID,'viewCategoryDetails_categoryName')))
        time.sleep(1)
        doc_page=self.driver.page_source
        cats=self.get_values(doc_page,i="viewCategoryDetails_categoryName")
        for c in cats:
            #doc_cat=self.driver.find_element_by_xpath('/html/body/div[1]/div[6]/div[1]/section/form[1]/table/tbody/tr[2]/td[2]/select')
            doc_cat=WebDriverWait(self.driver, t).until(presence_of_element_located((By.ID,'viewCategoryDetails_categoryName')))
            time.sleep(1)
            doc_cat.send_keys(c)
            time.sleep(1)
            #self.driver.find_element_by_xpath('/html/body/div[1]/div[6]/div[1]/section/form[1]/table/tbody/tr[3]/td[2]/select')
            WebDriverWait(self.driver, t).until(presence_of_element_located((By.XPATH,'/html/body/div[1]/div[6]/div[1]/section/form[1]/table/tbody/tr[3]/td[2]/select')))
            time.sleep(1)
            years_page=self.driver.page_source
            dates=self.get_values(years_page,i="viewCategoryDetails_finacialYear")
            for y in dates:
                years=self.driver.find_element_by_xpath('/html/body/div[1]/div[6]/div[1]/section/form[1]/table/tbody/tr[3]/td[2]/select')
                years=WebDriverWait(self.driver, t).until(presence_of_element_located((By.XPATH,'/html/body/div[1]/div[6]/div[1]/section/form[1]/table/tbody/tr[3]/td[2]/select')))
                time.sleep(1)
                years.send_keys(str(y))
                submit2=self.driver.find_element(By.ID,'viewCategoryDetails_0')
                try:
                    time.sleep(1)
                    strt=time.time()
                    submit2.click()
                    time.sleep(1)
                    dur=time.time()-strt
                    if dur>20:
                        self.driver.refresh()
                    table_page=self.driver.page_source
                    data=self.get_data(table_page,cin)
                    dataframe=pd.DataFrame(data)
                    df=pd.concat([df,dataframe],axis=0,ignore_index=True)
                except:
                    time.sleep(1)
                    WebDriverWait(self.driver, t).until(presence_of_element_located((By.ID,'msgboxclose')))
                    popup=self.driver.find_element(By.ID,'msgboxclose') 
                    #popup=WebDriverWait(self.driver, 10).until(element_to_be_clickable((By.XPATH,'/html/body/div[1]/div[6]/div[1]/section/div[2]/a'))) 
                    time.sleep(0.5)
                    popup.click()
                
            if df is not None:
                data_dict=df.to_dict('records')
                md._insert(data_dict)
def runner(prox,cin_list):
    scrp=Scrapper(URL,prox)
    print(threading.current_thread(),cin_list)
    for cin in cin_list:
        print(cin)
        scrp.scrap(cin)

def main():
    prox=GetProxy(PROXY_URL)
    scrp=Scrapper(URL,prox)
    n_cins=len(CINS)
    print(n_cins)
    for cin in CINS:
        print(cin)
        scrp.scrap(cin)
    '''
    for i in range(0,n_cins,n_ips):
        strt=i
        end=min(n_cins,i+n_ips)
        x=threading.Thread(target=runner,args=(prox,CINS[strt:end]))
        x.start()
        threads.append(x)
    '''
    

if __name__ == "__main__":
    main()
    

