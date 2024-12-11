import requests
import time
import json
import re
import yaml
from datetime import datetime, timedelta
import time
import sys
import os
import subprocess

# 结束程序
# sys.exit()

def find_script_by_keyword(exported_url, config):
    """
    根据查询的 URL 返回对应的 Script 名称。

    参数:
        exported_url (str): 导出的 URL，格式为 "export jd_lzkj_draw_url=...".
        config (str): 配置内容，YAML 格式的字符串。

    返回:
        str 或 None: 找到的 Script 名称，或 None 如果未找到。
    """
    try:
        # 从 export 语句中提取关键字
        keyword = exported_url.split('=')[0].split()[-1]

        # 解析 YAML 配置内容
        data = yaml.safe_load(config)

        # 遍历所有条目以查找匹配的关键字
        for item in data.get('js_config', []):
            if 'KeyWord' in item:
                # 将 KeyWord 转换为统一的列表形式
                keywords_list = item['KeyWord'] if isinstance(item['KeyWord'], list) else [item['KeyWord']]
                
                # 遍历每个关键字列表
                for kw_group in keywords_list:
                    # 如果 kw_group 是列表，逐个检查是否有匹配的关键字
                    if isinstance(kw_group, list):
                        if keyword in kw_group:
                            return item.get('Script')  # 返回匹配的 Script 名称
                    # 如果 kw_group 不是列表，直接检查关键字匹配
                    elif keyword == kw_group:
                        return item.get('Script')

    except Exception as e:
        # 处理异常并打印错误信息
        print(f"发生错误: {e}")

    # 如果未找到匹配项，返回 None
    return None



def fetch_url_with_retries(url, max_retries=3, retry_delay=2):
    """尝试获取指定 URL 的内容，支持重试机制。

    Args:
        url (str): 要访问的 URL。
        max_retries (int): 最大重试次数。
        retry_delay (int): 每次重试之间的延迟（秒）。

    Returns:
        str or None: 成功时返回网页内容，失败时返回 None。
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            # 检查状态码是否为 200
            if response.status_code == 200:
                #print("状态码: 200")
                #print("内容长度:", len(response.text))
                return response.text  # 返回网页内容
            else:
                print("请求未成功，状态码:", response.status_code)
                return None
        except requests.exceptions.RequestException as e:
            print(f"请求出错: {e}")
            if attempt < max_retries - 1:  # 如果还有重试机会
                print(f"等待 {retry_delay} 秒后重试... (尝试 {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)  # 等待一段时间再重试
            else:
                print("所有重试均已失败。")
                return None  # 返回 None

def extract_env_variable(env_string):
    """从给定字符串中提取环境变量名及其值"""
    if env_string is None:
        print("输入的 env_string 是 None，请检查传入的参数。")
        return None, None
    
    # 正则表达式模式
    pattern = r'^export\s+(\w+)=["\']?([^"\']+)["\']?;?$'
    
    match = re.match(pattern, env_string.strip())
    
    if match:
        var_name = match.group(1)  # 提取变量名
        value = match.group(2)      # 提取变量值
        return var_name, value
    else:
        return None, None

def check_and_wait(start_time):
    """
    计算已用时间和剩余等待时间，并决定是否需要等待。
    
    :param start_time: 循环开始时的时间
    :return: None
    """
    elapsed_time = (datetime.now() - start_time).total_seconds()  # 计算循环运行时间
    wait_time = DEFAULT_WAIT_TIME * 60 - elapsed_time  # 计算剩余等待时间（转换为秒）
    
    # 如果剩余等待时间大于0，则等待
    if wait_time > 0:
        print(f"等待 {wait_time:.2f} 秒...")
        time.sleep(wait_time)
    else:
        print("循环运行时间超过5分钟，立即进入下一个循环。")



def should_execute(target_days, target_hour):
    """判断当前日期和小时是否符合执行条件"""
    now = datetime.now()
    return now.day in target_days and now.hour == target_hour

# 每月执行的日期和时间
execution_days = {1, 15, 28}  # 每月的 1 日、15 日、28 日
target_hour = 10  # 设定为10点

# 使用示例 更新  Faker.spy
# 目标 URL 和本地文件路径
#url = 'https://raw.githubusercontent.com/shufflewzc/AutoSpy/master/config/Faker.spy' 
url = 'https://raw.githubusercontent.com/free-diy/spy/54c5a4d4d926ea38b479e837d342f62c6c295f26/config/9r.spy' 

local_file_path = 'Faker.spy'  # 假设文件与脚本在同一目录下

# 使用示例
if should_execute(execution_days, target_hour):
    content = fetch_url_with_retries(url)
    
    if content:
        # 检查文件大小
        if len(content) > 0:  # 假设我们只需确保文件不是空的
            # 检查文件内容
            keywords = ['js_config', 'KeyWord', 'Env']
            if check_content(content, keywords):
                # 替换本地文件
                with open(local_file_path, 'wb') as local_file:
                    local_file.write(content)
                print(f"文件 {local_file_path} 已成功更新。")
            else:
                print("下载的文件不包含所需的关键字。")
        else:
            print("下载的文件为空。")
#else:
    #print("今天不是执行操作的时间。")



def read_yaml_file(file_path):
    """从指定文件读取YAML内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()  # 读取文件内容
            return content  # 返回原始 YAML 内容
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
        return None
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None

# 指定文件路径
local_file_path = 'Faker.spy'

# 读取 Faker.spy  YAML 文件内容
yaml_spy = read_yaml_file(local_file_path)



# url = 'https://telegram.xinces001.filegear-sg.me/latest-date' 

# url = 'https://raw.githubusercontent.com/shufflewzc/AutoSpy/master/config/Faker.spy' 
#   测试发现这个更新快 https://raw.githubusercontent.com/free-diy/spy/54c5a4d4d926ea38b479e837d342f62c6c295f26/config/9r.spy

#  https://t.me/s/faketoulu?before=
 

# 默认等待时间为5分钟（直接以分钟为单位）
DEFAULT_WAIT_TIME = 10  # 5分钟

while True:
    # 记录开始时间
    start_time = datetime.now()
    
    # 获取当前时间和分钟数
    now = datetime.now()
    current_minute = now.minute
    
    # 打印当前时间和分钟数（可选）
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}，当前分钟数: {current_minute}")
    
    # 检查当前分钟数是否大于 50
    if current_minute > 50:
        print("当前分钟数大于 50，退出循环。")
        break

    url = 'https://telegram.xinces001.filegear-sg.me/latest-date' 
    content = fetch_url_with_retries(url)  # 获取最新消息的时间
    
    # 设置 content_time 为一个很小的时间
    content_time = datetime(2000, 1, 1)  # 设定为一个很早的时间
    
    if content:  # 确保 content 不为 None
        try:
            # 尝试将字符串转换为 datetime 对象
            content_time = datetime.strptime(content, "%Y-%m-%d %H:%M:%S")
            print(f"返回的最新消息时间为: {content_time}")
        except ValueError:
            print(f"'{content}' 返回的最新消息时间 不符合时间格式")
            # 调用函数判断是否需要等待
            check_and_wait(start_time)
    else:
        print("获取内容失败，无法进行时间解析。")
        # 调用函数判断是否需要等待
        check_and_wait(start_time)



    # 计算最近10分钟的时间
    time_limit = now - timedelta(minutes=DEFAULT_WAIT_TIME)

    # 判断 content_time 是否在最近10分钟之内
    if content_time < time_limit:  # 在10分钟前
        print("content 不在最近10分钟之内。")
        # 调用函数判断是否需要等待
        check_and_wait(start_time)
    
    # 格式化时间为所需的格式
    formatted_time = time_limit.strftime("%Y-%m-%d %H:%M:%S")
        
    # 将空格替换为%20以符合URL编码
    url_encoded_time = formatted_time.replace(" ", "%20")
        
    # 构建最终的URL参数字符串
    result = f"/?date={url_encoded_time}"
    #print(result)
    url = 'https://telegram.xinces001.filegear-sg.me' + result

    content = fetch_url_with_retries(url)
    #print(url)
    #print(content)  

    # 提前定义默认值
    data = []  # 或者 data = [] 如果需要默认为空列表

    if content:  # 确保 content 不为 None
        try:
            # 将 content 解析为 Python 对象
            data = json.loads(content)
            #print("成功解析 JSON 数据:", data)
        except json.JSONDecodeError:
            print("解析 JSON 数据失败，内容可能不是有效的 JSON 格式:", content)
    else:
        print("获取内容失败，无法进行 JSON 解析。")  
     
    #print(data)  
    # 提取 fullLink 并去掉多余的引号
    #links = [item['fullLink'] for item in data if 'fullLink' in item]
    links = [item['fullLink'] for item in data if isinstance(data, list) and 'fullLink' in item] if isinstance(data, list) else []
    # 输出结果
    for link in links:
        print(link)
        script_name = find_script_by_keyword(link, yaml_spy)
        #print(script_name)

        variable_name, variable_value = extract_env_variable(link)
        if script_name and variable_name and variable_value is not None:
            if '/' in script_name:
                script_name = script_name.split('/')[-1]
            print(f"提取成功: 脚本名={script_name}, 变量名={variable_name}, 值={variable_value}")
           
            # 调用方法来修改环境变量
            os.environ[variable_name] = variable_value

            #command = f"task shufflewzc_faker2_main/{script_name}"
            command = f"task 6dylan6_jdm/{script_name}"
            print(f"运行: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            print("输出:", result.stdout)
            #print("错误:", result.stderr)
            #print("返回码:", result.returncode)
            print()
            time.sleep(6)
            #sys.exit()

        else:
            print("提取失败")
        print()
        
    #sys.exit()
    #time.sleep(3)
   
    # 调用方法来修改环境变量
    # os.environ[keyword] = value

    #sys.exit()
    
    # 调用函数判断是否需要等待
    check_and_wait(start_time)

 
  









