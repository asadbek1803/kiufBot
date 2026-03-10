import logging
import requests
import re
import time
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# URLs
LOGIN_URL = "https://student.ukiu.uz/dashboard/login"
CAPTCHA_URL = "https://student.ukiu.uz/dashboard/captcha"
TIMETABLE_URL = "https://student.ukiu.uz/education/time-table"
PROFILE_URL = "https://student.ukiu.uz/student/profile"
DASHBOARD_URL = "https://student.ukiu.uz/dashboard"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Browser-like headers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "uz-UZ,uz;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
    "Pragma": "no-cache",
    "DNT": "1",
}


def create_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session


def get_hemis_captcha(session: requests.Session) -> Tuple[Optional[str], Optional[bytes], Optional[Dict]]:

    try:

        logger.info("Fetching login page...")

        response = session.get(
            LOGIN_URL,
            headers={
                **DEFAULT_HEADERS,
                "Referer": LOGIN_URL
            },
            timeout=10
        )

        response.raise_for_status()

        logger.info(f"Login page status: {response.status_code}")

        csrf_patterns = [
            r'name="_csrf-frontend" value="(.+?)"',
            r'name="csrf-token" content="(.+?)"',
            r'csrf-token" content="(.+?)"'
        ]

        csrf = None

        for pattern in csrf_patterns:
            match = re.search(pattern, response.text)
            if match:
                csrf = match.group(1)
                logger.info(f"CSRF token found using pattern: {pattern}")
                break

        if not csrf:
            logger.error("CSRF token not found")
            return None, None, None

        logger.info(f"CSRF token: {csrf[:20]}...")

        time.sleep(1)

        logger.info("Fetching captcha...")

        captcha_response = session.get(
            CAPTCHA_URL,
            headers={
                **DEFAULT_HEADERS,
                "Referer": LOGIN_URL
            },
            timeout=10
        )

        captcha_response.raise_for_status()

        cookies = session.cookies.get_dict()

        logger.info(f"Captcha received: {len(captcha_response.content)} bytes")

        return csrf, captcha_response.content, cookies

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while getting captcha: {e}")
        return None, None, None

    except Exception as e:
        logger.error(f"Unexpected error in captcha: {e}")
        return None, None, None


def hemis_login(session, csrf, login, password, captcha_code):

    login_data = {
        "_csrf-frontend": csrf,
        "FormStudentLogin[login]": login,
        "FormStudentLogin[password]": password,
        "FormStudentLogin[reCaptcha]": captcha_code
    }

    headers = {
        **DEFAULT_HEADERS,
        "Referer": LOGIN_URL,
        "Origin": "https://student.ukiu.uz",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = session.post(
        LOGIN_URL,
        data=login_data,
        headers=headers,
        allow_redirects=True,
        timeout=10
    )

    if "login" not in response.url.lower():
        return True, None

    text = response.text.lower()

    if "captcha" in text:
        return False, "Captcha noto'g'ri"

    if "kiritgan ma’lumotlaringizni tekshirib bo‘lmadi" in text:
        return False, "Login yoki parol noto'g'ri"

    return False, "Login amalga oshmadi"


def fetch_schedule(session: requests.Session, week_id: str = None):

    url = TIMETABLE_URL

    if week_id:
        url = f"{TIMETABLE_URL}?week={week_id}"

    logger.info(f"Fetching schedule from: {url}")

    response = session.get(
        url,
        headers={
            **DEFAULT_HEADERS,
            "Referer": DASHBOARD_URL
        },
        allow_redirects=True,
        timeout=10
    )

    if "login" in response.url.lower():
        logger.error("Session expired or login failed")
        return []

    if response.status_code != 200:
        logger.error(f"Schedule page error: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    parsed_lessons = []

    days = soup.select("div.box.box-success.sh")

    logger.info(f"Found {len(days)} days")

    for day in days:

        day_title_elem = day.select_one(".box-title")
        raw_day_title = day_title_elem.text.strip() if day_title_elem else "Unknown"
        day_title = raw_day_title.split("\n")[0].strip()

        lessons = day.select("li.list-group-item")

        for lesson in lessons:

            time_node = lesson.select_one(".pull-right")
            lesson_time = time_node.text.strip() if time_node else ""

            text = lesson.text.replace(lesson_time, "").strip()

            lines = [line.strip() for line in text.split("\n") if line.strip()]

            subject = lines[0] if len(lines) > 0 else ""
            room = lines[1] if len(lines) > 1 else ""
            lesson_type = lines[2] if len(lines) > 2 else ""
            teacher = lines[3] if len(lines) > 3 else ""

            pair_match = re.search(r'(\d+)-juftlik', subject)
            pair_number = int(pair_match.group(1)) if pair_match else 0

            parsed_lessons.append({
                "day": day_title,
                "pair_number": pair_number,
                "subject": subject,
                "teacher": teacher,
                "room": room,
                "lesson_type": lesson_type,
                "lesson_time": lesson_time
            })

    return parsed_lessons


def get_student_group(session: requests.Session) -> Optional[str]:

    try:

        response = session.get(
            DASHBOARD_URL,
            headers={
                **DEFAULT_HEADERS,
                "Referer": LOGIN_URL
            },
            timeout=10
        )

        if response.status_code == 200:

            soup = BeautifulSoup(response.text, "html.parser")

            user_role_span = soup.find("span", class_="user-role")

            if user_role_span and user_role_span.text:
                group = user_role_span.text.strip()
                logger.info(f"Found group: {group}")
                return group

            group_patterns = [
                r'Guruh:\s*([A-Z0-9\-]+)',
                r'Group:\s*([A-Z0-9\-]+)'
            ]

            for pattern in group_patterns:
                match = re.search(pattern, response.text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()

        return None

    except Exception as e:
        logger.error(f"Error getting group: {e}")
        return None


def get_current_week_id(session):

    response = session.get(
        TIMETABLE_URL,
        headers={
            **DEFAULT_HEADERS,
            "Referer": DASHBOARD_URL
        }
    )

    soup = BeautifulSoup(response.text, "html.parser")

    options = soup.select("select option")

    now = datetime.now()

    months = {
        "yanvar":1, "fevral":2, "mart":3, "aprel":4,
        "may":5, "iyun":6, "iyul":7, "avgust":8,
        "sentabr":9, "oktabr":10, "noyabr":11, "dekabr":12
    }

    for opt in options:

        text = opt.text.lower().strip()

        match = re.findall(r'(\d{1,2})\s*(\w+)', text)

        if len(match) < 2:
            continue

        start_day, start_month = match[0]
        end_day, end_month = match[1]

        start_date = datetime(
            now.year,
            months.get(start_month, now.month),
            int(start_day)
        )

        end_date = datetime(
            now.year,
            months.get(end_month, now.month),
            int(end_day)
        )

        if start_date <= now <= end_date:
            return opt.get("value")

    return None