import subprocess,os, glob
from pprint import pprint as ppt
import html
from html5print import HTMLBeautifier

import pdb
import json

from termcolor import colored, cprint


def sortHtmlfromJson(fpath):
    res = "<html lang='en'><head><meta charset='UTF-8'></head><body>"
    with open(fpath) as f:
        ccontent = json.load(f)
    res = res + "<h1>" + ccontent['title']+ "</h1>" 
    res = res + "<div>" + ccontent['content']+ "</div>" 
    res = res + "</body></html>"
    return [res, ccontent['title']]

def genHtml(fpath):
    # IoC prepration
    # Note
    indres = "<html lang='en'><head><meta charset='UTF-8'></head><body>"
    indres = indres + "<h1> 书籍目录 </h1>" 
    # subprocess.run("", shell=True, check=True)

    # Sorting all existed files
    for c in [_ for _ in sorted(os.listdir(fpath)) if _.endswith('json') ]:
        res = sortHtmlfromJson(fpath+c)
        indres = indres + "<div class='index'><a href='"+c.split('.')[0]+".html'>"+ res[1] +"</a></div>"
        with open(r'%s.html'%(fpath+c.split('.')[0]), 'w', encoding='utf8') as fp:
            fp.write(res[0])
            fp.flush()

    indres = indres + "</body></html>"
    with open(r'%s/index.html'%(fpath), 'w', encoding='utf8') as fp:
        fp.write(indres)
        fp.flush()
    return 0

def genEpubfromHtml(fpath):
    # Gen Html
    genHtml(fpath+'/dumps/')
    # Got book info
    cinfo = {}
    try:
        with open(fpath+'/bookinfo') as f:
            cinfo  = json.load(f)
        # Note
        cprint("ebookmaker --make epub.images --cover '%s/cover.jpg' --title '%s' --author '%s' --max-depth 2 %s/dumps/index.html --output-file %s"%(fpath, cinfo['name'], cinfo['author'],fpath,fpath+"/dumps/"+cinfo['name']), 'green', attrs=['dark'])
        subprocess.run("ebookmaker --make epub.images --cover '%s/cover.jpg' --title '%s' --author '%s' --max-depth 2 %s/dumps/index.html --output-file %s"%(fpath, cinfo['name'], cinfo['author'],fpath,fpath+"/dumps/"+cinfo['name']), shell=True, check=True)
        subprocess.run("mv %s-images-epub.epub %s/%s.epub"%(fpath+"/dumps/"+cinfo['name'],fpath, cinfo['name']), shell=True, check=True)
        cprint("生成ePub完成 (/%s/%s.epub)"%(fpath,cinfo['name']),'blue',attrs=['bold'])
        return 0
    except:
        return -1

if __name__=='__main__':
    pass
