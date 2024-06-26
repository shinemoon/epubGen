import subprocess,os, glob
import requests
from pprint import pprint as ppt
import html
from pyquery import PyQuery as pq
from fake_useragent import UserAgent

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

from genepub import genEpubfromHtml

from url_normalize import url_normalize

from urllib.parse import urlparse

# Add Spider based solution:

from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider
from scrapy import Request

from epubscrapy.epubscrapy.spiders import epubgen as epubspider



def is_absolute_url(url):
    return (url[0]=='/')

def detectRealUrl(url, baseurl):
    res = url
    if(is_absolute_url(url)):
        res = siteConfigs['url']+url
    elif(url[0:7]=='http://' or url[0:8]=='https://'):
        res = url
    else:
        res = baseurl[0:baseurl.rindex('/')+1]+url
    return res




def getSingle(url,ind):
    fId = "%04d_%s"%(ind,hashlib.sha1(url.encode("utf-8")).hexdigest()[:10])
    results = requests.get(url, headers=headers)
    if(results.status_code==200):
        rencoding = results.encoding
        results.encoding='utf-8'
        doc = pq(results.text)
        ctitle = doc(siteConfigs['titleKey']).text()
        for k in siteConfigs['excludeKeys']:
            doc(k).remove()
        tunedContent = doc(siteConfigs['contentKey']).html()
        dumpContent = {
            # Title
            'title':ctitle,
            # Content
            'content':tunedContent,
            # url
            'url':url,
        }

        #ppt(dumpContent)
        with open(r'working/'+wId+'/dumps/'+fId +'.json', 'w') as fp:
            json.dump(dumpContent,fp,ensure_ascii = False)
            fp.flush()
        return 0
    else:
        return -1



def fetchContent(refresh):
    # Logged list
    hlist = []
    # Index List
    ilist = []

    # Gap List
    glist = []
    # to log 'real' id of workinglist
    idlist = []
    try:
        with open(r'working/'+wId+'/workingList', 'r', encoding='utf-8') as fp:
            cprint("读取目录列表完成",'blue',attrs=['dark'])
            ilist = json.load(fp)
    except:
            cprint("工作列表读取失败",'red',attrs=['bold'])
            return -1

    if(refresh==False):
        cprint("继续以前历史下载",'blue',attrs=['dark'])
        # Need to sort out worklist corss compare the workingList vs. updatedList
        try:
            with open(r'working/'+wId+'/updatedList', 'r', encoding='utf-8') as fp:
                cprint("读取历史列表完成",'blue',attrs=['dark'])
                hlist = json.load(fp)
                for i in range(len(ilist)):
                    if ilist[i] not in hlist:
                        glist.append(ilist[i])
                        idlist.append(i)
        except:
                cprint("历史列表读取失败,请重新建立",'red',attrs=['bold'])
                return fetchContent(True)
    else:
        subprocess.run("rm -f working/"+wId+"/updatedList", shell=True, check=True)
        subprocess.run("rm -f working/"+wId+"/dumps/*", shell=True, check=True)
        glist = ilist
        idlist = [i for i in range(len(ilist))]
        cprint("重新开始下载所有",'blue',attrs=['dark'])

    cprint("开始获取正文",'light_blue',attrs=['bold'])
    print(glist)
    for i in glist:
        print(i['title'])

    listSize = len(glist)
    errCount = 0

    with trange(listSize) as t:
        t.set_description(colored('开始获取','light_cyan',attrs=['dark']))
        for i in t:    
            res = 0
            singleUrl = glist[i]['url']
            global indexPage
            res = getSingle(detectRealUrl(singleUrl, indexPage),i)
            sleep(siteConfigs['fetchDelay'])
            if(res!=-1):
                hlist.append(glist[i])
                t.set_description(colored('获取第 %i 篇. 存入文件'%(i+1),'light_cyan',attrs=['dark']))
            else:
                errCount=errCount+1
                t.set_description(colored("提取第%i篇失败"%i,'red',attrs=['bold']));
            try:
                with open(r'working/'+wId+'/updatedList', 'w', encoding='utf-8') as fp:
                    json.dump(hlist,fp,ensure_ascii = False)
                    fp.flush()
            except:
                cprint("工作列表刷新失败",'light_yellow',attrs=['dark'])
        cprint("获取完成,共"+str(listSize)+"篇，其中失败"+str(errCount)+"篇。",'light_blue',attrs=['bold'])
    return 0 

def parseIndex(url):
    cprint("创建工作目录",'blue',attrs=['dark'])
    subprocess.run("mkdir -p working/"+wId+"/dumps", shell=True, check=True)
    ilist=[]
    indList=[]
    blist=[]
    doc = None

    # sub def
    def getList(url):
        cprint("开始刷新目录:%s"%(url),'light_blue',attrs=['dark'])
        res = None
        results = requests.get(url, headers=headers)
        if(results.status_code==200):
            rencoding = results.encoding
            results.encoding = 'utf-8'
            # Try just print
            content = html.escape(results.text)
            # pyQuery
            doc = pq(results.text)
            # to fetch full list
            res = doc(siteConfigs['indexKey'])
        return (res,doc)

    (curList,doc) = getList(url)
    blist = blist + curList 

    if('indexList' in siteConfigs.keys()):
        # There is select list for some sites!
        # Get the index page list:
        cprint("多页目录存在，开始拉取目录页",'yellow')
        olist = doc(siteConfigs['indexList'])
        for i in olist:
            iurl = i.values()[0]
            iurl = detectRealUrl(iurl,url) 
            indList.append(iurl)
        for c in indList:
            (curList,doc) = getList(c)
            blist = blist + curList 
    else:
        pass

    if(blist != None):
        ilen = len(blist)

        #to fetch cover picture
        try:
            picurl = url_normalize(doc(siteConfigs['fmimg']).attr('src'))
            picurl = detectRealUrl(picurl, url)

            picraw = requests.get(picurl)
            with open(r'working/'+wId+'/rawcover.jpg', 'wb') as f:
                f.write(picraw.content)
                f.flush()
        except Exception as e:
            cprint(repr(e),'white',attrs=['dark'])
            # placeholder for default pic
            subprocess.run("cp cover.jpg working/%s/rawcover.jpg"%(wId),shell=True, check=True)
            cprint("无封面图片，采用自动生成",'red',attrs=['dark'])
        # sort the book info
        binfo = {
                'name':doc(siteConfigs['bookName']).text(),
                'author':doc(siteConfigs['authorName']).text()
                }
        with open(r'working/'+wId+'/bookinfo', 'w', encoding='utf-8') as fp:
            json.dump(binfo,fp,ensure_ascii = False)
            fp.flush()

        if(debugFlag):
            ilen = debugSample
        for b in range(ilen):
            #pdb.set_trace()
            ilist.append({
                'title':blist[b].text,
                'url':blist[b].get('href'),
                'fId':"%04d_%s"%(b,hashlib.sha1((siteConfigs['url']+blist[b].get('href')).encode("UTF-8")).hexdigest()[:10]),
            })
        # Create table cache
        try:
            with open(r'working/'+wId+'/workingList', 'w', encoding='utf-8') as fp:
                json.dump(ilist,fp,ensure_ascii = False)
                fp.flush()
        except:
            cprint("工作列表创建失败列表完成",'red',attrs=['dark'])
            exit(1)
        return 0 
    else:
        exit(1)


# Refresh Working List

# Start/Resume to fetch content

if __name__=='__main__':
    global bookId, indexPage, wId

    # Debug Flag
    debugFlag = False
    debugSample = 8 
    # Config Relavant
    siteConfigs = {}

    # Initialization of parser
    parser = argparse.ArgumentParser()
    parser.add_argument("bookId", help="目录页ID(指去掉网站根地址之后的部分，包括'/')")
    parser.add_argument("-c","--clean", help="清空工作目录,此指令与其他互斥", action="store_true")
    parser.add_argument("-n","--newindex", help="重新刷新目录", action="store_true")
    parser.add_argument("-r","--refresh", help="从头开始下载文章", action="store_true")
    parser.add_argument("-t","--toc", help="令目录可见", action="store_true")
    parser.add_argument("-m","--mail", help="发送邮件,需要在配置文件填入接受邮箱地址",action="store_true")
    args = parser.parse_args()



    # use EmptyBorderType to "disable" borders until a proper enhancement is added to console-menu
    menu_format = MenuFormatBuilder().set_border_style(EmptyBorderStyle())
    m_desc = "网络小说电子书生成工具"
    if(debugFlag):
        m_desc = m_desc + "  [* Debug Mode ON]"
    menu = ConsoleMenu(m_desc, "请选择站点", exit_option_text="退出")
    menu.formatter = menu_format
    def buildMenu(name):
        if(name==''):
            exit(0)
        global siteConfigs
        with open('configs/'+name+'.json') as f:
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

    # Clean?
    if(args.clean):
        cprint("清空目录",'red',attrs=['dark'])
        subprocess.run("rm -rf working/%s"%(wId),shell=True, check=True)
        exit(0)


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
    fetchContent(args.refresh)

    binfo = {}
    # 生成Epub
    try:
        with open(r'working/'+wId+'/bookinfo', 'r', encoding='utf-8') as fp:
            binfo = json.load(fp)
    except:
        cprint("未能成功读取目录页面",'red')
        exit(1)

    if(genEpubfromHtml('working/'+wId, siteConfigs,args)==0):
        # to check if mail needed:
        if(args.mail):
            cprint("生成完毕，发送邮件!",'green',attrs=['bold'])
            # Reconstruct the sendmail bash
            mailcmd = "./send-mail.sh %s %s %s"%(siteConfigs['recmail'],'working/'+wId+'/'+binfo['name']+'.epub',binfo['name'])
            # excute the sendmail cmd
            cprint(mailcmd,'green',attrs=['dark'])
            subprocess.run(mailcmd,shell=True, check=True)
        else:
            cprint("生成完毕！",'green',attrs=['bold'])
