# selenium_utils.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

def fetch_rendered_html(url, wait_time=5):
    """
    Uses Selenium to fetch the fully rendered HTML of the given URL.

    Args:
      url (str): The URL of the webpage.
      wait_time (int): Time in seconds to wait for the page to fully load.

    Returns:
      str: The rendered HTML content or None if an error occurred.
    """
    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

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
