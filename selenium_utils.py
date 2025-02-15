from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

def fetch_rendered_html(url, wait_time=5):
    """
    Uses Selenium to fetch the fully rendered HTML of the given URL.
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')
    
    # Use the chromedriver installed by the system package.
    service = Service(executable_path="/usr/bin/chromedriver")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        # Wait for the page to render.
        time.sleep(wait_time)
        rendered_html = driver.page_source
        return rendered_html
    except Exception as e:
        print(f"Error fetching rendered HTML with Selenium: {e}", flush=True)
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
