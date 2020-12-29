from bs4 import BeautifulSoup
import requests
from random import choice
class GetProxy:
    def __init__(self,url,txt):
        self.url=url
        self.txt=txt
    def get_proxies(self):
        with open(self.txt,'r') as f:
            proxies=f.read().split('\n')
        proxy_list=[p.split(':')[0]+':'+p.split(':')[1] for p in proxies[:-1]]
        return choice(proxy_list)
    def get_proxy(self,):
        r=requests.get(self.url)
        soup=BeautifulSoup(r.content,'html5lib')
        tds=soup.find_all('td')[::8]
        ips=list(map(lambda x:x[0]+':'+x[1] if x[2]=='India' else None,list(zip(map(lambda x:x.text,tds),map(lambda x:x.text,soup.find_all('td')[1::8]),
        map(lambda x:x.text,soup.find_all('td')[3::8])))))
        ips=[ip for ip in ips if ip]
        proxy={'https':choice(ips)}
        return proxy['https']
