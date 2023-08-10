import requests
import pprint
import html
from pyquery import PyQuery as pq
from fake_useragent import UserAgent
from html5print import HTMLBeautifier

import pdb
import json

from time import sleep
from tqdm import tqdm,trange

from termcolor import colored, cprint

# Config Relavant
siteConfigs = {
        'name':'香书小说',
        'url':'https://www.ibiquges.info',
        'indexKey':'#list dd a',
        }


# Preparing of Requests
ua = UserAgent()
random_user_agent = ua.random
headers = {
    "User-Agent": random_user_agent
}

bookId = '/5/5395/'
indexPage = siteConfigs['url']+bookId

def fetchContent(start):
    cprint("开始获取正文,从第"+str(int(start+1))+"篇开始",'light_blue',attrs=['bold'])
    ilist = []
    # Create table cache
    try:
        with open(r'workingList', 'r', encoding='utf8') as fp:
            cprint("读取列表完成",'blue',attrs=['dark'])
            ilist = json.load(fp)
            #pprint.pprint(ilist)
    except:
            cprint("工作列表读取失败",'red',attrs=['bold'])
            return -1
    with trange(len(ilist)) as t:
        for i in t:    
            t.set_description(colored('正在获取第 %i 篇' % i,"light_cyan"))
            sleep(0.01)
        cprint("获取完成,共"+str(int(i+1))+"篇",'light_blue',attrs=['bold'])
    return 0 

def parseIndex(url):
    ilist=[]
    results = requests.get(indexPage, headers=headers)
    results.encoding='utf-8'
    if(results.status_code==200):
        # Try just print
        #content = html.escape(results.text)
        #print(HTMLBeautifier.beautify(content, 4))
    
        # pyQuery
        doc = pq(results.text)
        blist = doc(siteConfigs['indexKey'])
        for b in range(len(blist)):
            ilist.append({
                'title':blist.eq(b).text(),
                'url':blist.eq(b).attr('href'),
            })

        # Create table cache
        try:
            with open(r'workingList', 'w', encoding='utf8') as fp:
                json.dump(ilist,fp,ensure_ascii = False)
            print("WorkingList Create Done.")
        except:
            print("WorkingList Create Failed.")
        return 0 
    else:
        print("Failed to get valid page!")
        return -1

        #pdb.set_trace()

# Refresh Working List
#parseIndex(indexPage)

# Start/Resume to fetch content
fetchContent(0)

