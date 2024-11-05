# 1. 检验网站功能正常 --用户注册 --普通用户登录 --普通用户上传 --普通用户下载
# 2. WAF检验 --恶意payload  -- 随机header
# 运行方法 ： python check.py [YOUR_HOST] [YOUR_PORT]   --->python check.py 127.0.0.1 5000
import sys
import time
import requests
import random
import string
from bs4 import BeautifulSoup
from imapclient import IMAPClient
import email
from email.header import decode_header
import re

host = sys.argv[1]
port = int(sys.argv[2])

Uurl = 'http://' + host + ':' + str(port)
login_url = Uurl + '/auth/login'
captcha_url = Uurl +'/auth/captcha/email'
signup_url = Uurl + '/auth/register'
logout_url = Uurl + '/auth/logout'
upload_page_url = Uurl + '/file/upload'
download_url = Uurl + '/file/download'
feedback_url = Uurl + '/file/submit_feedback'  
view_fb_url = Uurl + '/file/view_feedback'

login_session = requests.Session()
response = login_session.get(login_url)
soup = BeautifulSoup(response.text, 'html.parser')
csrf_token_tag = soup.find('input', {'name': 'csrf_token'})
csrf_token = csrf_token_tag['value']

def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def getCaptcha():
    # 电子邮件账户配置
    EMAIL = "efgwnwqwhuo@163.com"
    PASSWORD = "ZWPBXUHUMWUIRZTT"
    IMAP_SERVER = "imap.163.com"

    server = IMAPClient("imap.163.com", ssl=True, port=993)
    server.login(EMAIL, PASSWORD)

    server.id_({"name": "IMAPClient", "version": "2.1.0"})

    messages = server.select_folder('INBOX')
    # print('1',messages)
    messages = server.search('ALL')
    # print('2',messages)
    latest_email_id = messages[-1]

    # 获取最新的邮件
    response = server.fetch(latest_email_id, ['RFC822'])
    raw_email = response[latest_email_id][b'RFC822']
    msg = email.message_from_bytes(raw_email)

    # 解析邮件内容
    def get_verification_code(email_message):
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    return extract_code_from_text(body)
        else:
            body = email_message.get_payload(decode=True).decode()
            return extract_code_from_text(body)

    # 从邮件内容中提取验证码
    def extract_code_from_text(text):
            code_match = re.search(r"\b\d{6}\b", text)
            if code_match:
                return code_match.group(0)
            return None

    # 获取验证码
    verification_code = get_verification_code(msg)
    server.logout()
    return verification_code


# WAF check with random headers
def check_waf( url,csrf_token):
    waf_test_payloads = [
        "' OR '1'='1",
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>",
        "<iframe src='javascript:alert(1)'></iframe>",
        "; cat /etc/passwd",
        "'; SELECT SLEEP(10); --"
    ]
    
    for payload in waf_test_payloads:
        headers = {
            'User-Agent': random_string(50),
            'Referer': random_string(30),
            'X-Forwarded-For': random_string(12)
        }
        data = {'username': payload, 'password': 'password', 'csrf_token': csrf_token}
        
        if "upload" in url:
            files = {'file': ('test.txt', payload)}
            response = login_session.post(url, data=data, files=files, headers=headers)
        else:
            response = login_session.post(url, data=data, headers=headers)

        if response.status_code == 200 and any(p in response.text for p in waf_test_payloads):
            # print(response.text)
            raise Exception('WAF Check Failed: No WAF detected for payload: ' + payload+url)
    
    return True

# checkLogin
def checklogin(username, pswd, csrf_token):
    login_data = {
        'username': username,
        'password': pswd,
        'csrf_token': csrf_token
    }
    login_response = login_session.post(login_url, data=login_data)
    return login_response

def checkSignup(csrf_token):
    email = 'efgwnwqwhuo@163.com'
    login_session.get(captcha_url + '?email=efgwnwqwhuo@163.com')
    time.sleep(2)
    captcha = getCaptcha()
    signup_data = {
        'csrf_token':csrf_token,
        'email':email,
        'captcha':captcha,
        'username':'wozaiceshi',
        'password':'WOzaiceshi1.',
        'password_confirm':'WOzaiceshi1.'
    }
    # print('AAAAAAAAAAAAaa',captcha)
    signup_response = login_session.post(signup_url,data=signup_data)
    # print('signup',login_session.cookies)
    return signup_response

# checklogout
def checklogout():
    response = login_session.get(logout_url)
    return response

# checkUpload
def checkupload(filename, description, csrf_token):
    files = {
        'file': open(filename, 'rb')
    }
    upload_data = {
        'csrf_token': csrf_token,
        'description': description
    }
    upload_data_response = login_session.post(upload_page_url, data=upload_data, files=files)
    return upload_data_response

# checkDownload
def download_file(filename, filetype):
    params = {
        'filename': filename,
        'type': filetype
    }
    response = login_session.get(download_url, params=params)
    return response

# check submitfeedback
def submitfeedback( csrf_token):
    msg = random_string(100)
    data = {
        'csrf_token':csrf_token,
        'message':msg
    }
    response = login_session.post(feedback_url,data)
    # print ('1',session.cookies)
    return response

# check viewfeedback
def viewfeedback(csrf_token):
    data = {
        'csrf_token':csrf_token
    }
    response = login_session.post(view_fb_url,data)
    return response


# check
def check(host):
    try:            
        # ==============================================================
        # ==============    Check Original User Function    ============
        # ==============================================================

        # # Check signup
        # login_response = checkSignup( csrf_token)
        # # print(login_session.cookies)

        # # print(response.status_code)
        # # print(response.text)
        # if login_response.status_code != 200:
        #     raise Exception('ERROR: There is an error in the website SIGNUP logic...')   
        
        # Check signup
        response = checklogin('wozaiceshi', 'WOzaiceshi1.', csrf_token)
        # print(response.text)
        if '用户未注册' in response.text:
            login_response = checkSignup( csrf_token)
            if login_response.status_code != 200:
                raise Exception('ERROR: There is an error in the website SIGNUP logic...') 
            else: 
                print('SIGNUP FUNCTION RUNS WELL...')
        
                response = checklogin('wozaiceshi', 'WOzaiceshi1.', csrf_token)
        # print(response.text)
        if '用户未注册' in response.text:
            login_response = checkSignup( csrf_token)
            if login_response.status_code != 200:
                raise Exception('ERROR: There is an error in the website SIGNUP logic...') 
            else: 
                print('SIGNUP FUNCTION RUNS WELL...')
            # raise Exception('ERROR: There is an error in the website LOGIN logic...')
        # print(login_session.cookies)

        # Check login
        response = checklogin('wozaiceshi', 'WOzaiceshi1.', csrf_token)
        if response.status_code != 200:
            raise Exception('ERROR: There is an error in the website LOGIN logic...')
        else: 
            print('LOGIN FUNCTION RUNS WELL...')

        # Check submit feedback -- This is permitted ONLY BY VIP!!!
        response = submitfeedback(csrf_token)
        # print(response.status_code)
        # print(response.text)
        if (response.status_code != 200 ) or ('只有管理员有权限访问此页面' not in response.text):
            raise Exception('ERROR: There is an error in the website FEEDBACK logic...')
        else: 
            print('SUBMIT_FEEDBACK FUNCTION RUNS WELL...')

        # Check view feedback -- This is permitted ONLY BY VIP!!!
        response = viewfeedback(csrf_token)
        if (response.status_code != 200 ) or ('只有管理员有权限访问此页面' not in response.text):
            raise Exception('ERROR: There is an error in the website FEEDBACK logic...')
        else: 
            print('VIEW_FEEDBACK FUNCTION RUNS WELL...')

        with open('NJS.txt', 'w') as file:
            file.write('NEWJEANS IS EVERYWHERE.....HELPING YOU TO TEST FUNCTIONS...\n')

        # Check upload
        response = checkupload('./NJS.txt', '火力全开', csrf_token)
        if response.status_code != 200:
            raise Exception('ERROR: There is an error in the website UPLOAD logic...')
        # print(response.status_code)   
        # print(response.text)

        # Check download
        filetypes = ['encrypted', 'hashvalue', 'plaintext', 'signature']
        for filetype in filetypes:
            response = download_file('./NJS.txt', filetype)
            if response.status_code != 200:
                raise Exception(f'ERROR: There is an error in the website function logic for {filetype} downloading...')
            else: 
                print(f'UPLOAD {filetype} FUNCTION RUNS WELL...')

        # Check logout
        response = checklogout()
        if response.status_code != 200:
            raise Exception('ERROR: There is an error in the website LOGOUT logic...')
        else: 
            print('LOGOUT FUNCTION RUNS WELL...')

        # print(response.status_code)
        # print(response.text)

        # ==============================================================
        # ================      Check Web Service      =================
        # ==============================================================

        # Perform WAF check with both methods for all URLs
        urls_to_check = [login_url, upload_page_url, download_url]
        for url in urls_to_check:
            waf_result_random_headers = check_waf(url,csrf_token)
            if not waf_result_random_headers:
                raise Exception(f'WAF check with random headers failed for {url}')
            else:
                print('WEB SERVICE UNIVERSAL PROTECTION CHECK PASSED')
            
        login_session.close()

        return (True, "IP: " + host + " OK")
    except Exception as e:
        return (False, "IP: " + host + " is down, " + str(e))

print(check(host))