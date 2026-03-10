import requests
import re
from bs4 import BeautifulSoup
import time

LOGIN_URL = "https://student.ukiu.uz/dashboard/login"
CAPTCHA_URL = "https://student.ukiu.uz/dashboard/captcha"

def test_login():
    session1 = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    session1.headers.update(headers)
    
    r = session1.get(LOGIN_URL)
    csrf = re.search(r'name="_csrf-frontend" value="(.+?)"', r.text).group(1)
    
    time.sleep(1)
    captcha = session1.get(CAPTCHA_URL)
    with open("test_captcha.jpg", "wb") as f:
        f.write(captcha.content)
        
    cookies_dict = session1.cookies.get_dict()
    print("Fetched CSRF and cookies:", cookies_dict)
    
    captcha_code = input("Enter captcha from test_captcha.jpg: ")
    
    # Simulate step 2 (new session)
    session2 = requests.Session()
    session2.headers.update(headers)
    requests.utils.add_dict_to_cookiejar(session2.cookies, cookies_dict)
    
    login_data = {
        "_csrf-frontend": csrf,
        "FormStudentLogin[login]": "495251100645",
        "FormStudentLogin[password]": "Asadbek.077", # Dummy or real if known? Using my own test
        "FormStudentLogin[reCaptcha]": captcha_code,
    }
    
    post_headers = {
        "Referer": LOGIN_URL,
        "Origin": "https://student.ukiu.uz",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    resp = session2.post(LOGIN_URL, data=login_data, headers=post_headers, allow_redirects=True)
    if "login" not in resp.url:
        print("Success! URL:", resp.url)
    else:
        print("Fail! Text contains captcha:", "captcha" in resp.text.lower())
        
if __name__ == "__main__":
    test_login()
