import logging
import requests
import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Tuple, Optional
import time

# Constants
LOGIN_URL = "https://student.ukiu.uz/dashboard/login"
CAPTCHA_URL = "https://student.ukiu.uz/dashboard/captcha"
TIMETABLE_URL = "https://student.ukiu.uz/education/time-table"
PROFILE_URL = "https://student.ukiu.uz/student/profile"
DASHBOARD_URL = "https://student.ukiu.uz/dashboard"

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_session() -> requests.Session:
    """
    Create browser-like session with appropriate headers
    
    Returns:
        requests.Session: Configured session object
    """
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "uz,ru;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }
    
    session.headers.update(headers)
    return session


def get_hemis_captcha(session: requests.Session) -> Tuple[Optional[str], Optional[bytes], Optional[Dict]]:
    """
    Get CSRF token and captcha image from HEMIS
    
    Args:
        session (requests.Session): Active session
        
    Returns:
        Tuple[Optional[str], Optional[bytes], Optional[Dict]]: (csrf_token, captcha_image_bytes, cookies)
    """
    try:
        # Get login page to extract CSRF token
        logger.info("Fetching login page...")
        response = session.get(LOGIN_URL, timeout=10)
        response.raise_for_status()
        
        # Log response status
        logger.info(f"Login page status: {response.status_code}")
        
        # Extract CSRF token using regex
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
            logger.error("CSRF token not found in login page")
            return None, None, None
        
        logger.info(f"CSRF token: {csrf[:20]}...")
        
        # Small delay to ensure captcha is fresh
        time.sleep(1)
        
        # Get captcha image
        logger.info("Fetching captcha...")
        captcha_response = session.get(CAPTCHA_URL, timeout=10)
        captcha_response.raise_for_status()
        
        logger.info(f"Captcha received: {len(captcha_response.content)} bytes")
        
        # Get cookies
        cookies = session.cookies.get_dict()
        logger.info(f"Cookies: {cookies}")
        
        return csrf, captcha_response.content, cookies
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while getting captcha: {e}")
        return None, None, None
    except Exception as e:
        logger.error(f"Unexpected error in get_hemis_captcha: {e}")
        return None, None, None


def hemis_login(session, csrf, login, password, captcha_code):

    login_data = {
        "_csrf-frontend": csrf,
        "FormStudentLogin[login]": login,
        "FormStudentLogin[password]": password,
        "FormStudentLogin[reCaptcha]": captcha_code
    }

    headers = {
        "Referer": LOGIN_URL,
        "Origin": "https://student.ukiu.uz",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = session.post(
        LOGIN_URL,
        data=login_data,
        headers=headers,
        allow_redirects=True
    )

    # LOGIN_URL is ".../dashboard/login", so checking for "dashboard" implies it's always true.
    # Instead, we check if we actually left the login page.
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
        allow_redirects=True,
        timeout=10
    )

    # LOGIN PAGE GA REDIRECT BO‘LSA
    if "login" in response.url.lower():
        logger.error("Session expired or login failed - redirected to login.")
        return []

    if response.status_code != 200:
        logger.error(f"Schedule page error: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    parsed_lessons = []

    days = soup.select("div.box.box-success.sh")

    logger.info(f"Found {len(days)} days in schedule")

    for day in days:

        day_title_elem = day.select_one(".box-title")
        raw_day_title = day_title_elem.text.strip() if day_title_elem else "Unknown"
        # Often looks like "Seshanba\n 10 mart, 2026", we just want "Seshanba"
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
    """
    Get student group from dashboard
    
    Args:
        session (requests.Session): Active authenticated session
        
    Returns:
        Optional[str]: Group name or None if failed
    """
    try:
        # First try dashboard
        response = session.get(DASHBOARD_URL, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # First, check for <span class="user-role">INT-A-25</span>
            user_role_span = soup.find("span", class_="user-role")
            if user_role_span and user_role_span.text:
                group = user_role_span.text.strip()
                logger.info(f"Found group via user-role: {group}")
                return group
                
            # Try to find group in various places
            group_patterns = [
                r'Guruh:\s*([A-Z0-9\-]+)',
                r'Group:\s*([A-Z0-9\-]+)',
                r'<div[^>]*>Guruh<\/div>\s*<div[^>]*>([^<]+)<\/div>'
            ]
            
            for pattern in group_patterns:
                match = re.search(pattern, response.text, re.IGNORECASE)
                if match:
                    group = match.group(1).strip()
                    logger.info(f"Found group: {group}")
                    return group
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting student group: {e}")
        return None


def check_login_status(session: requests.Session) -> bool:
    """
    Check if session is still authenticated
    
    Args:
        session (requests.Session): Session to check
        
    Returns:
        bool: True if still authenticated, False otherwise
    """
    try:
        # Try to access dashboard (protected page)
        response = session.get(DASHBOARD_URL, timeout=10, allow_redirects=False)
        
        # If redirected to login page, session is invalid
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.headers.get("Location", "")
            if "login" in location.lower():
                logger.info("Session expired - redirected to login")
                return False
        
        # Check if we got the dashboard page
        if response.status_code == 200 and "dashboard" in response.url.lower():
            logger.info("Session is valid")
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error checking login status: {e}")
        return False

from datetime import datetime
from bs4 import BeautifulSoup
import re

def get_current_week_id(session):

    response = session.get(TIMETABLE_URL)

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

        # masalan: "09 mart / 14 mart"
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