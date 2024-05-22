import os,json

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

def read_working_list(wId):
    # 定义文件路径
    file_path = os.path.join('working', wId, 'workingList')

    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在。")
        return None

    # 读取 JSON 文件中的字典列表
    try:
        with open(file_path, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            return data
    except json.JSONDecodeError:
        print(f"文件 {file_path} 不是有效的 JSON 格式。")
        return None
