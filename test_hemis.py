import requests
import re
from bs4 import BeautifulSoup

LOGIN_URL = "https://student.ukiu.uz/dashboard/login"
CAPTCHA_URL = "https://student.ukiu.uz/dashboard/captcha"

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
session.headers.update(headers)

r = session.get(LOGIN_URL)
csrf = re.search(r'name="_csrf-frontend" value="(.+?)"', r.text).group(1)

print("CSRF:", csrf)
captcha = session.get(CAPTCHA_URL)
with open("test_captcha.jpg", "wb") as f:
    f.write(captcha.content)

print("Cookies sent in requests:")
for cookie in session.cookies:
    print(cookie.name, cookie.value)
