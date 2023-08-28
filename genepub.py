import subprocess,os, glob
from pprint import pprint as ppt
import html
from html5print import HTMLBeautifier

import pdb
import json

from termcolor import colored, cprint

import random


def sortHtmlfromJson(fpath):
    with open(fpath) as f:
        ccontent = json.load(f)

    res = "<h1 style='font-size:1.1em'>" + ccontent['title']+ "</h1>" 
    res = res + "<div>" + ccontent['content']+ "</div>" 
    return [res, ccontent]

def genHtml(fpath):
    cfg={}
    with open(fpath+'/../bookinfo') as f:
        cfg = json.load(f)
    # Page prepration
    indres = "<html lang='zh'><head><meta charset='UTF-8'><style> \
            </style></head><body>"
    # Sorting all existed files
    for c in [_ for _ in sorted(os.listdir(fpath)) if _.endswith('json') ]:
        res = sortHtmlfromJson(fpath+c)
        indres = indres + res[0]

    indres = indres + "</body></html>"

    
    with open(r'%s/index.html'%(fpath), 'wb') as fp:
        fp.write(HTMLBeautifier.beautify(indres, 4).encode('utf-8'))
        fp.flush()

    return 0


def genEpubfromHtml(fpath,cfg):
    # Gen Html
    genHtml(fpath+'/dumps/')

    # Prepare cover
    mkcover = ""

    # Check Type of Cover:
    if(('fmtype' not in cfg.keys()) or cfg['fmtype']=='default'):
        # Emboss?
        mkcover = mkcover + "gm convert -border 3x3 -bordercolor 'rgba(100,100,100,0.01)' "+fpath+"/rawcover.jpg tmp/cover.jpg;"
        # Composite
        randCover = random.choice(['A','B','C'])
        mkcover = mkcover + "gm composite -gravity southwest  tmp/cover.jpg cover"+randCover+".jpg "+fpath+"/cover.jpg;rm -rf tmp/*;"
        print(mkcover)
        subprocess.run(mkcover, shell=True, check=True)

    # Got book info
    cinfo = {}
    try:
        with open(fpath+'/bookinfo') as f:
            cinfo  = json.load(f)
        epubCmd = "ebook-convert %s/dumps/index.html %s/%s.epub \
        --authors='%s' \
        --level1-toc='//*[name()=\"h1\" or name()=\"h2\"]'\
        --preserve-cover-aspect-ratio \
        --book-producer epubGen \
        --language Chinese \
        --pretty-print \
        --output-profile tablet \
        --max-levels=0 \
        --title='%s' \
        " % (fpath, fpath, cinfo['name'], cinfo['author'], cinfo['name'])

        if(os.path.exists("%s/cover.jpg"%(fpath))):
            epubCmd = epubCmd + "--cover %s/cover.jpg "%(fpath)

        #cprint(epubCmd,'white',attrs=['dark'])
        subprocess.run(epubCmd, shell=True, check=True)
        cprint("生成ePub完成 (/%s/%s.epub)"%(fpath,cinfo['name']),'blue',attrs=['bold'])
        return 0
    except Exception as e:
        cprint(repr(e),'white',attrs=['dark'])
        cprint("生成ePub失败 (/%s/%s.epub)"%(fpath,cinfo['name']),'red',attrs=['bold'])
        return -1

if __name__=='__main__':
    pass
