import subprocess,os, glob
from pprint import pprint as ppt
import html
from html5print import HTMLBeautifier 
import pdb
import json

from termcolor import colored, cprint

import random

from PIL import Image


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
    # Index Page prepration
    indres = "<html lang='zh'><head><meta charset='UTF-8'><style> \
            </style></head><body>"

    # Sorting all existed files
    for c in [_ for _ in sorted(os.listdir(fpath)) if _.endswith('json') ]:
        res = sortHtmlfromJson(fpath+c)
        ### Folder style
        ## Write single pages
#        singlec = "<html lang='zh'><head><meta charset='UTF-8'><style></style></head><body>"
#        singlec = singlec+res[0]
#        singlec = singlec + "</body></html>"
#        with open(r'%s/%s.html'%(fpath,c), 'wb') as fp:
#            fp.write(HTMLBeautifier.beautify(singlec, 4).encode('utf-8'))
#            fp.flush()
#        # Prepare index and link
#        indres = indres + "<a href='"+c+".html'>"+res[1]["title"]+"</a>"


        ### Single File style
        indres = indres + res[0]

    indres = indres + "</body></html>"
    
    with open(r'%s/index.html'%(fpath), 'wb') as fp:
        fp.write(HTMLBeautifier.beautify(indres, 4).encode('utf-8'))
        fp.flush()

    return 0

def genCover(fpath,cfg, binfo):
    # Got materials' info:
    rawwidth = 0
    rawheight = 0

    basewidth = 0
    baseheight = 0
    mkcover = ""
    mkcover = mkcover + "convert -resize 300 "+fpath+"/rawcover.jpg tmp/cover.jpg;"
    subprocess.run(mkcover, shell=True, check=True)
    ## real cover:
    with Image.open('tmp/cover.jpg') as f:
        # get width and height
        rawwidth = f.width
        rawheight = f.height

    # Prepare cover
    mkcover = ""
    # Check Type of Cover:
    if(('fmtype' not in cfg.keys()) or cfg['fmtype']=='default'):
        # Directly use the raw cover
        subprocess.run("cp "+fpath+"/rawcover.jpg "+fpath+"/cover.jpg;", shell =True, check=True)
    elif(cfg['fmtype']=='refine'):
        # Composite
        randCover = random.choice(['A','B','C'])
        ## Base cover:
        with Image.open('cover'+randCover+'.jpg') as f:
            # get width and height
            basewidth = f.width
            baseheight = f.height

        # To confirm the canva size:
        cwidth = basewidth -  rawwidth
        cheight = rawheight
        sizeStr = str(cwidth)+"x"+str(cheight)
        
        mkcover = mkcover + "convert  -fill 'rgba(0,0,0,0.6)' -draw 'rectangle 0,%d %d,%d' cover%s.jpg tmp/bgcover.jpg;"%((baseheight-rawheight)/2,basewidth,(baseheight+rawheight)/2,randCover)
        mkcover = mkcover + "convert -gravity east -kerning 15 -font title.ttf -fill '#EEEEEE' -pointsize 120 -annotate +%d+0 '%s' tmp/bgcover.jpg tmp/bgcover.jpg;"%(60,binfo['name'][:9])
        mkcover = mkcover + "convert  -fill 'rgba(0,0,0,0.8)' -draw 'rectangle 0,%d %d,%d' tmp/bgcover.jpg tmp/bgcover.jpg;"%((baseheight/2+rawheight/2+100),basewidth,(baseheight/2+rawheight/2+200))
        mkcover = mkcover + "convert -gravity west -fill 'lightblue' -kerning 5 -font title.ttf -pointsize 60 -annotate +60+%d '%s' tmp/bgcover.jpg tmp/bgcover.jpg;"%((rawheight/2+150) ,binfo['author'][:10])
        mkcover = mkcover + "convert -gravity southeast -fill '#555555' -kerning 2 -pointsize 30 -annotate +20+10 '@epubGen' tmp/bgcover.jpg tmp/bgcover.jpg;"
        mkcover = mkcover + "composite -gravity west -geometry +20+0 tmp/cover.jpg tmp/bgcover.jpg "+fpath+"/cover.jpg;rm tmp/* -rf;"
        subprocess.run(mkcover, shell=True, check=True)


def genEpubfromHtml(fpath,cfg):
    # Gen Html
    genHtml(fpath+'/dumps/')


    # Got book info
    cinfo = {}
    try:
        with open(fpath+'/bookinfo') as f:
            cinfo  = json.load(f)

        # Gen Cover
        genCover(fpath,cfg,cinfo)

        epubCmd = "ebook-convert %s/dumps/index.html %s/%s.epub \
        --authors='%s' \
        --level1-toc='//*[name()=\"h1\" or name()=\"h2\"]'\
        --preserve-cover-aspect-ratio \
        --book-producer epubGen \
        --language Chinese \
        --pretty-print \
        --input-encoding 'utf-8'\
        --output-profile tablet \
        --max-levels=1 \
        --title='%s' \
        " % (fpath, fpath, cinfo['name'], cinfo['author'], cinfo['name'])

        if(os.path.exists("%s/cover.jpg"%(fpath))):
            epubCmd = epubCmd + "--cover %s/cover.jpg "%(fpath)

        cprint(epubCmd,'white',attrs=['dark'])
        subprocess.run(epubCmd, shell=True, check=True)
        cprint("生成ePub完成 (/%s/%s.epub)"%(fpath,cinfo['name']),'blue',attrs=['bold'])
        return 0
    except Exception as e:
        cprint(repr(e),'white',attrs=['dark'])
        cprint("生成ePub失败 (/%s/%s.epub)"%(fpath,cinfo['name']),'red',attrs=['bold'])
        return -1

if __name__=='__main__':
    pass
