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
    return res

def genHtml(fpath):
    # Sorting all existed files
    for c in [_ for _ in os.listdir(fpath) if _.endswith('json') ]:
        res = sortHtmlfromJson(fpath+c)
        with open(r'%s.html'%(fpath+c), 'w', encoding='utf8') as fp:
            fp.write(res)
    return 0

def genEpubfromHtml(fpath):
    # Note
    res = "<html lang='en'><head><meta charset='UTF-8'></head><body>"
    res = res + "<h1> 书籍目录 </h1>" 
    res = res + "<div>"
    res = res + "</div>" 
    res = res + "</body></html>"
    # subprocess.run("", shell=True, check=True)
    return 0


if __name__=='__main__':
    pass
