"""Utility for scraping data from ukiu.uz website"""

import aiohttp
from bs4 import BeautifulSoup
from typing import Optional, Dict, List


class UKIUScraper:
    """Scraper for ukiu.uz website"""
    
    BASE_URL = "https://ukiu.uz"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _fetch_page(self, url: str, lang: str = "uz") -> Optional[str]:
        """Fetch page content"""
        try:
            session = await self._get_session()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None
    
    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content"""
        return BeautifulSoup(html, 'html.parser')
    
    async def get_admission_info(self, lang: str = "uz") -> str:
        """Get admission information"""
        url = f"{self.BASE_URL}/{lang}/qabul/"
        html = await self._fetch_page(url, lang)
        
        if not html:
            return ""
        
        soup = self._parse_html(html)
        
        # Try to find main content
        content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if content:
            # Get text content, remove scripts and styles
            for script in content(['script', 'style']):
                script.decompose()
            
            text = content.get_text(separator='\n', strip=True)
            # Limit length
            return text[:3000] if len(text) > 3000 else text
        
        return ""
    
    async def get_university_info(self, lang: str = "uz") -> str:
        """Get university information"""
        url = f"{self.BASE_URL}/{lang}/about"
        html = await self._fetch_page(url, lang)
        
        if not html:
            # Try home page
            url = f"{self.BASE_URL}/{lang}/"
            html = await self._fetch_page(url, lang)
        
        if not html:
            return ""
        
        soup = self._parse_html(html)
        
        # Try to find main content
        content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if content:
            for script in content(['script', 'style']):
                script.decompose()
            
            text = content.get_text(separator='\n', strip=True)
            return text[:3000] if len(text) > 3000 else text
        
        return ""
    
    async def get_address(self, lang: str = "uz") -> str:
        """Get university address"""
        url = f"{self.BASE_URL}/{lang}/contact"
        html = await self._fetch_page(url, lang)
        
        if not html:
            return "Toshkent shahri" if lang == "uz" else ("Tashkent city" if lang == "en" else "Город Ташкент")
        
        soup = self._parse_html(html)
        
        # Look for address in common locations
        address_selectors = [
            'address',
            '.address',
            '#address',
            '[class*="address"]',
            '[class*="contact"]',
        ]
        
        for selector in address_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return "Toshkent shahri" if lang == "uz" else ("Tashkent city" if lang == "en" else "Город Ташкент")
    
    async def get_faculties(self, lang: str = "uz") -> List[Dict[str, str]]:
        """Get list of faculties"""
        url = f"{self.BASE_URL}/{lang}/faculties"
        html = await self._fetch_page(url, lang)
        
        if not html:
            return []
        
        soup = self._parse_html(html)
        
        faculties = []
        # Try to find faculty cards or links
        faculty_elements = soup.find_all(['a', 'div'], class_=lambda x: x and 'faculty' in x.lower() if x else False)
        
        for elem in faculty_elements[:10]:  # Limit to 10
            name = elem.get_text(strip=True)
            link = elem.get('href', '')
            if name:
                faculties.append({
                    'name': name,
                    'link': link if link.startswith('http') else f"{self.BASE_URL}{link}"
                })
        
        return faculties
    
    async def get_directions(self, lang: str = "uz") -> List[Dict[str, str]]:
        """Get list of directions/specialties"""
        url = f"{self.BASE_URL}/{lang}/directions"
        html = await self._fetch_page(url, lang)
        
        if not html:
            return []
        
        soup = self._parse_html(html)
        
        directions = []
        # Try to find direction cards or links
        direction_elements = soup.find_all(['a', 'div'], class_=lambda x: x and ('direction' in x.lower() or 'specialty' in x.lower()) if x else False)
        
        for elem in direction_elements[:10]:  # Limit to 10
            name = elem.get_text(strip=True)
            link = elem.get('href', '')
            if name:
                directions.append({
                    'name': name,
                    'link': link if link.startswith('http') else f"{self.BASE_URL}{link}"
                })
        
        return directions


# Global scraper instance
scraper = UKIUScraper()

