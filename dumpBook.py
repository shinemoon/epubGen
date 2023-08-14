import subprocess,os, glob
import requests
from pprint import pprint as ppt
import html
from pyquery import PyQuery as pq
from fake_useragent import UserAgent
from html5print import HTMLBeautifier

import pdb
import json

from time import sleep
from tqdm import tqdm,trange

from termcolor import colored, cprint
import hashlib
import random


import argparse

from consolemenu import *
from consolemenu.items import *
from consolemenu.format import *
from consolemenu.menu_component import Dimension
from ui import EmptyBorderStyle
def getSingle(url,ind):
    fId = "%03d_%s"%(ind,hashlib.sha1(url.encode("UTF-8")).hexdigest()[:10])
    results = requests.get(url, headers=headers)
    results.encoding='utf-8'
    if(results.status_code==200):
        doc = pq(results.text)
        for k in siteConfigs['excludeKeys']:
            doc(k).remove()
        dumpContent = {
            # Title
            'title':doc(siteConfigs['titleKey']).text(),
            # Content
            'content':(doc(siteConfigs['contentKey']).text()),
            # url
            'url':url,
        }

        #pdb.set_trace()
        #ppt(dumpContent)
        with open(r'working/'+wId+'/dumps/'+fId, 'w', encoding='utf8') as fp:
            json.dump(dumpContent,fp,ensure_ascii = False)
        return 0
    else:
        return -1



def fetchContent(resume):
    # Logged list
    hlist = []
    # Index List
    ilist = []

    # Gap List
    glist = []
    try:
        with open(r'working/'+wId+'/workingList', 'r', encoding='utf8') as fp:
            cprint("读取目录列表完成",'blue',attrs=['dark'])
            ilist = json.load(fp)
    except:
            cprint("工作列表读取失败",'red',attrs=['bold'])
            return -1

    if(resume):
        cprint("继续以前历史下载",'blue',attrs=['dark'])
        # Need to sort out worklist corss compare the workingList vs. updatedList
        try:
            with open(r'working/'+wId+'/updatedList', 'r', encoding='utf8') as fp:
                cprint("读取历史列表完成",'blue',attrs=['dark'])
                hlist = json.load(fp)
        except:
                cprint("工作列表读取失败",'red',attrs=['bold'])
                return -1
        glist = [item for item in ilist if item not in hlist]
    else:
        subprocess.run("rm -f working/"+wId+"/updatedList", shell=True, check=True)
        subprocess.run("rm -f working/"+wId+"/dumps/*", shell=True, check=True)
        glist = ilist
        cprint("重新开始下载所有",'blue',attrs=['dark'])

    cprint("开始获取正文",'light_blue',attrs=['bold'])
    for i in glist:
        print(i['title'])

    listSize = len(glist)
    errCount = 0

    with trange(listSize) as t:
        t.set_description(colored('开始获取','light_cyan',attrs=['dark']))
        for i in t:    
            res = 0
            if(debugFlag):
                res = getSingle(siteConfigs['url']+glist[i]['url'],i)
            sleep(siteConfigs['fetchDelay'])
            if(res!=-1):
                hlist.append(glist[i])
                t.set_description(colored('获取第 %i 篇. 存入文件'%(i+1),'light_cyan',attrs=['dark']))
            else:
                errCount=errCount+1
                t.set_description(colored("提取第%i篇失败"%i,'red',attrs=['bold']));
            try:
                with open(r'working/'+wId+'/updatedList', 'w', encoding='utf8') as fp:
                    json.dump(hlist,fp,ensure_ascii = False)
            except:
                cprint("工作列表刷新失败",'light_yellow',attrs=['dark'])
        cprint("获取完成,共"+str(listSize)+"篇，其中失败"+str(errCount)+"篇。",'light_blue',attrs=['bold'])
    return 0 

def parseIndex(url):
    cprint("开始刷新目录",'light_blue',attrs=['bold'])
    cprint("创建工作目录",'blue',attrs=['dark'])
    subprocess.run("mkdir -p working/"+wId+"/dumps", shell=True, check=True)
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
        ilen = len(blist)

        #to fetch cover picture

        if(debugFlag):
            ilen = debugSample
        for b in range(ilen):
            ilist.append({
                'title':blist.eq(b).text(),
                'url':blist.eq(b).attr('href'),
                'fId':"%03d_%s"%(b,hashlib.sha1((siteConfigs['url']+blist.eq(b).attr('href')).encode("UTF-8")).hexdigest()[:10]),
            })
        # Create table cache
        try:
            with open(r'working/'+wId+'/workingList', 'w', encoding='utf8') as fp:
                json.dump(ilist,fp,ensure_ascii = False)
        except:
            cprint("工作列表创建失败列表完成",'red',attrs=['dark'])
            exit(1)
        return 0 
    else:
        print("Failed to get valid page!")
        return -1


# Refresh Working List

# Start/Resume to fetch content

if __name__=='__main__':
    global bookId, indexPage, wId

    # Debug Flag
    debugFlag = True
    debugSample = 10
    # Config Relavant
    siteConfigs = {}


    # Initialization of parser
    parser = argparse.ArgumentParser()
    parser.add_argument("bookId", help="目录页ID(指去掉网站根地址之后的部分，包括'/')")
    parser.add_argument("-n","--newindex", help="重新刷新目录", action="store_true")
    parser.add_argument("-r","--resume", help="继续未完成的任务", action="store_true")
    args = parser.parse_args()

    # use EmptyBorderType to "disable" borders until a proper enhancement is added to console-menu
    menu_format = MenuFormatBuilder().set_border_style(EmptyBorderStyle())
    menu = ConsoleMenu("网络小说电子书生成工具", "请选择站点", exit_option_text="退出")
    menu.formatter = menu_format
    def buildMenu(name):
        if(name==''):
            exit(0)
        global siteConfigs
        with open('configs/'+c) as f:
            siteConfigs = json.load(f)
    
    for c in [_ for _ in os.listdir('configs') if _.endswith('json')]:
        with open('configs/'+c) as f:
            ccfg = json.load(f)
        function_item = FunctionItem(ccfg['name'], buildMenu, [c.split('.')[0]], should_exit=True)
        menu.append_item(function_item)
    menu.show()

    # For Menuexit
    if(siteConfigs=={}):
        cprint("取消操作",'grey',attrs=['bold'])
        exit(0)
    
    # Preparing of Requests
    ua = UserAgent()
    random_user_agent = ua.random
    headers = {
        "User-Agent": random_user_agent
    }

    bookId = args.bookId
    indexPage = siteConfigs['url']+bookId
    wId = hashlib.sha1(indexPage.encode("UTF-8")).hexdigest()[:10];


    cprint("选择站点："+siteConfigs['name'] +".",'yellow',attrs=['bold'])
    # 目录处理
    if(args.newindex):
        cprint("重新刷新目录",'blue',attrs=['dark'])
        parseIndex(indexPage)
    else:
        if(os.path.exists('working/'+wId+'/workingList')):
            cprint("不刷新目录",'blue',attrs=['dark'])
        else:
            cprint("工作列表不存在，重新刷新列表",'blue',attrs=['bold'])
            parseIndex(indexPage)
    
    fetchContent(args.resume)

