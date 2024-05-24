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

def select_and_read_config(directory):


    def get_json_files(directory):
        """获取指定目录中的所有 JSON 文件"""
        return [f for f in os.listdir(directory) if f.endswith('.json')]
    
    def read_json_file(file_path):
        """读取 JSON 文件内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def prompt_user_choice(options):
        """提示用户选择一个选项"""
        for idx, option in enumerate(options, start=1):
            print(f"{idx}. {option['name']}")
        choice = int(input("请选择网站: "))
        return options[choice - 1]
    """提示用户选择配置文件并读取其内容"""
    json_files = get_json_files(directory)
    
    options = []
    for json_file in json_files:
        file_path = os.path.join(directory, json_file)
        data = read_json_file(file_path)
        data['file_path'] = file_path  # 将文件路径存储到字典中，以便后续使用
        options.append(data)

    selected_option = prompt_user_choice(options)
    
    selected_file_path = selected_option['file_path']
    selected_data = read_json_file(selected_file_path)
    
    return selected_data
