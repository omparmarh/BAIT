#!/usr/bin/env python3
"""
BAIT PRO ULTIMATE - Web Browser Agent
- Automated web browsing with Selenium
- Web scraping and data extraction
- Form automation
- Price tracking
- Research assistant
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Try Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False
    logging.warning("Selenium not available")

# Try BeautifulSoup
try:
    from bs4 import BeautifulSoup
    import requests
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    logging.warning("BeautifulSoup not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# WEB SCRAPER (Simple HTTP-based)
# ═══════════════════════════════════════════════════════════════

class WebScraper:
    """
    Simple web scraping with requests + BeautifulSoup
    """
    
    def __init__(self, user_agent: Optional[str] = None):
        """
        Initialize web scraper
        
        Args:
            user_agent: Custom user agent string
        """
        self.user_agent = user_agent or \
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        
        logger.info("Web Scraper initialized")
    
    def fetch(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetch web page content
        
        Args:
            url: URL to fetch
            timeout: Request timeout
            
        Returns:
            HTML content or None
        """
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Fetch error ({url}): {e}")
            return None
    
    def extract_text(self, html: str) -> str:
        """
        Extract text from HTML
        
        Args:
            html: HTML content
            
        Returns:
            Extracted text
        """
        if not HAS_BS4:
            return html
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_links(self, html: str, base_url: str = "") -> List[Dict[str, str]]:
        """
        Extract links from HTML
        
        Args:
            html: HTML content
            base_url: Base URL for relative links
            
        Returns:
            List of links with text and href
        """
        if not HAS_BS4:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            
            # Make absolute URL
            if href.startswith('/'):
                href = base_url.rstrip('/') + href
            
            links.append({'text': text, 'href': href})
        
        return links

# ═══════════════════════════════════════════════════════════════
# BROWSER CONTROLLER (Selenium-based)
# ═══════════════════════════════════════════════════════════════

class BrowserController:
    """
    Advanced browser automation with Selenium
    """
    
    def __init__(self, headless: bool = True, download_path: Optional[str] = None):
        """
        Initialize browser controller
        
        Args:
            headless: Run browser in headless mode
            download_path: Default download directory
        """
        if not HAS_SELENIUM:
            raise ImportError("Selenium is required for BrowserController")
        
        self.headless = headless
        self.download_path = download_path or os.path.expanduser("~/Downloads")
        self.driver = None
        
        logger.info("Browser Controller initialized")
    
    def start(self):
        """Start browser"""
        if self.driver:
            logger.warning("Browser already started")
            return
        
        options = Options()
        if self.headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        
        # Download preferences
        prefs = {
            'download.default_directory': self.download_path,
            'download.prompt_for_download': False
        }
        options.add_experimental_option('prefs', prefs)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            logger.info("Browser started")
        except Exception as e:
            logger.error(f"Browser start error: {e}")
            raise
    
    def stop(self):
        """Stop browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Browser stopped")
    
    def navigate(self, url: str):
        """Navigate to URL"""
        if not self.driver:
            self.start()
        
        self.driver.get(url)
        logger.info(f"Navigated to: {url}")
    
    def click(self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10):
        """
        Click element
        
        Args:
            selector: Element selector
            by: Selection method
            timeout: Wait timeout
        """
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        element.click()
        logger.info(f"Clicked: {selector}")
    
    def type_text(self, selector: str, text: str, by: By = By.CSS_SELECTOR, timeout: int = 10):
        """
        Type text into element
        
        Args:
            selector: Element selector
            text: Text to type
            by: Selection method
            timeout: Wait timeout
        """
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        element.clear()
        element.send_keys(text)
        logger.info(f"Typed into: {selector}")
    
    def get_text(self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> str:
        """
        Get element text
        
        Args:
            selector: Element selector
            by: Selection method
            timeout: Wait timeout
            
        Returns:
            Element text
        """
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element.text
    
    def extract_data(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract data from multiple elements
        
        Args:
            selectors: Dict of field_name -> selector
            
        Returns:
            Extracted data
        """
        data = {}
        for field, selector in selectors.items():
            try:
                data[field] = self.get_text(selector)
            except Exception as e:
                logger.warning(f"Could not extract {field}: {e}")
                data[field] = None
        
        return data
    
    def screenshot(self, filepath: str):
        """Take screenshot"""
        if self.driver:
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved: {filepath}")
    
    def execute_script(self, script: str) -> Any:
        """Execute JavaScript"""
        if self.driver:
            return self.driver.execute_script(script)

# ═══════════════════════════════════════════════════════════════
# BROWSER AGENT (Main Class)
# ═══════════════════════════════════════════════════════════════

class BrowserAgent:
    """
    Main browser agent for web automation tasks
    """
    
    def __init__(self, headless: bool = True):
        """
        Initialize browser agent
        
        Args:
            headless: Run browser in headless mode
        """
        self.scraper = WebScraper() if HAS_BS4 else None
        self.controller = BrowserController(headless=headless) if HAS_SELENIUM else None
        
        logger.info("Browser Agent initialized")
    
    def search_google(self, query: str) -> List[Dict[str, str]]:
        """
        Search Google and return results
        
        Args:
            query: Search query
            
        Returns:
            List of search results
        """
        if not self.controller:
            logger.error("Selenium not available")
            return []
        
        try:
            self.controller.start()
            self.controller.navigate(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            
            time.sleep(2)  # Wait for results
            
            # Extract results (simplified)
            results = []
            elements = self.controller.driver.find_elements(By.CSS_SELECTOR, 'h3')
            
            for elem in elements[:10]:
                try:
                    title = elem.text
                    link = elem.find_element(By.XPATH, './..').get_attribute('href')
                    results.append({'title': title, 'link': link})
                except:
                    pass
            
            return results
        finally:
            self.controller.stop()
    
    def scrape_page(self, url: str) -> Dict[str, Any]:
        """
        Scrape page content
        
        Args:
            url: Page URL
            
        Returns:
            Scraped data
        """
        if self.scraper:
            html = self.scraper.fetch(url)
            if html:
                return {
                    'text': self.scraper.extract_text(html),
                    'links': self.scraper.extract_links(html, url)
                }
        return {}
    
    def monitor_price(self, url: str, selector: str) -> Optional[float]:
        """
        Monitor product price
        
        Args:
            url: Product URL
            selector: CSS selector for price element
            
        Returns:
            Price value or None
        """
        if not self.controller:
            return None
        
        try:
            self.controller.start()
            self.controller.navigate(url)
            
            price_text = self.controller.get_text(selector)
            
            # Extract numeric price
            import re
            match = re.search(r'[\d,]+\.?\d*', price_text)price = float(match.group().replace(',', '')) if match else None
            
            return price
        except Exception as e:
            logger.error(f"Price monitoring error: {e}")
            return None
        finally:
            self.controller.stop()

# ═══════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════

def main():
    """Standalone testing"""
    print("=" * 60)
    print("BAIT Browser Agent - Test Mode")
    print("=" * 60)
    
    agent = BrowserAgent(headless=False)  # Visible for testing
    
    #Test search
    print("\n🔍 Testing Google search...")
    results = agent.search_google("Python programming")
    for i, result in enumerate(results[:5], 1):
        print(f"  {i}. {result['title']}")
    
    # Test scraping
    print("\n📄 Testing page scraping...")
    data = agent.scrape_page("https://www.example.com")
    if data.get('text'):
        print(f"  Extracted {len(data['text'])} characters")
        print(f"  Found {len(data.get('links', []))} links")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
