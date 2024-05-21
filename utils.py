def is_absolute_url(url):
    return (url[0]=='/')

def detectRealUrl(url, baseurl, siteConfigs):
    res = url
    if(is_absolute_url(url)):
        res = siteConfigs['url']+url
    elif(url[0:7]=='http://' or url[0:8]=='https://'):
        res = url
    else:
        res = baseurl[0:baseurl.rindex('/')+1]+url
    return res
