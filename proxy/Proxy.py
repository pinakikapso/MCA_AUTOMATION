from bs4 import BeautifulSoup
import requests
from random import choice
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
class GetProxy:
    def __init__(self,url):
        self.url=url
    def get_proxy(self):
        r=requests.get(self.url)
        proxies=r.content.decode('utf-8').split('\n')
        proxy_list=[p.split(':')[0]+':'+p.split(':')[1] for p in proxies]
        return choice(proxy_list[::-1])
    def getProxies(self):
        r = requests.get('https://free-proxy-list.net/')
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('tbody')
        proxies = []
        for row in table:
            if row.find_all('td')[4].text =='elite proxy' and  row.find_all('td')[6].text=='yes':
                proxy = ':'.join([row.find_all('td')[0].text, row.find_all('td')[1].text])
                proxies.append(proxy)
            else:
                pass
        return proxies
    

    

