import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from proxy.Proxy import GetProxy
from database.mongodb import Mongodb
import random
import urllib
md=Mongodb()
prox=GetProxy('https://free-proxy-list.net/')
with open('CINS.txt','r') as f:
    CINS=f.read().split('\n')
DATA={}
class Scrap:
    def __init__(self):
        self.s=requests.session()
        self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'}
        PROXY=random.choice(prox.getProxies())
        self.proxy={"https": PROXY}

        self.company_data={
            "companyOrllp":True,
            "cartType":"",
            "__checkbox_companyChk":True,
            "cinChk":True,
            "__checkbox_cinChk":True,
            "cinFDetails":"",
            "__checkbox_llpChk":True,
            "__checkbox_llpinChk":True,
            "__checkbox_regStrationNumChk":True,
            "countryOrigin":"INDIA",
            "__checkbox_stateChk":True,
            "displayCaptcha":False,
            "companyID":""	
            }
        self.category_data={
            "cinFDetails":"",
            "companyName":"",
            "cartType":"",
            "categoryName":	"",
            "finacialYear":""
            }
    def get_proxy(self):
        PROXY=random.choice(prox.getProxies())
        print(PROXY)
        return {"https": PROXY,"http":PROXY}
    def get_data(self,page,cins):
        soup=BeautifulSoup(page,'html.parser')
        results=soup.find(id='results')
        if results is None:
            return None
        data_list=[]
        for row in  results.find_all('tr'):
            if len(row('td'))!=0:
                    data_list.append({'Document Name':row('td')[0].text.replace('\t','').replace('\n','').replace('\r',''),
                    'Date of Filling':row('td')[1].text.replace('\t','').replace('\n','').replace('\r','')})
        return data_list
    def get_values(self,page,i):
        soup=BeautifulSoup(page,'html.parser')
        d=soup.find(id=i)
        if d is None:
            return None
        data=[opt['value'] for opt in d.find_all('option')]
        return data[1:]
    
    def extract(self,cin):
        print('CIN: ',cin)
        self.company_data["companyID"]=cin
        self.headers["Referer"]= 'http://www.mca.gov.in/mcafoportal/vpdDocumentCategoryDetails.do'
        r=self.s.post('http://www.mca.gov.in/mcafoportal/vpdCheckCompanyStatus.do',data=self.company_data,headers=self.headers)
        cats=self.get_values(r.content,"viewCategoryDetails_categoryName")
        years=self.get_values(r.content,"viewCategoryDetails_finacialYear")
        self.category_data["cinFDetails"]=cin
        if cats is None:
            print('Data not available')
            return 0
        DATA['CIN']=cin
        cat_data={}
        for c in cats:
            print('CATEGORY: ',c)
            cat_data[c]={}
            self.category_data["categoryName"]=c
            for y in years:
                cat_data[c][y]={}
                self.category_data["finacialYear"]=y
                r=self.s.post('http://www.mca.gov.in/mcafoportal/vpdDocumentCategoryDetails.do',data=self.category_data,headers=self.headers)
                data=self.get_data(r.content,cin)
                cat_data[c][y]=data
                if data:
                    md._insert(data)
        #DATA['CATEGORY_DATA']=cat_data
        #print(DATA)
        print("================================")
        return 1
def main():
    scrp=Scrap()
    total_time=0
    k=0
    for i,cin in enumerate(CINS):
        print('Total Companies: ',i)
        start=time.time()
        r=scrp.extract(cin)
        if r==1:
            total_time+=((time.time()-start)/60)
            print("----------------------------------------------------")
            print(f"Time taken for {cin}: {((time.time()-start)/60):4f}")
            print("----------------------------------------------------")
            if k%5==0:
                print("==========================================================")
                print(f"Total time taken after {k+1} companies: {total_time:4f}")
                print("==========================================================")
            k+=1
if __name__ == "__main__":
    main()
       



            



