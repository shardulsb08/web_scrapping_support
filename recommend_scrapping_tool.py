import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import time

# For Selenium (ensure you have Selenium and a browser driver installed)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def check_robots(url):
    """
    Checks the site's robots.txt file to determine if scraping is allowed.
    """
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        if not rp.can_fetch("*", url):
            print(f"Scraping disallowed by robots.txt at {robots_url}")
            return False
        else:
            print(f"Scraping allowed by robots.txt at {robots_url}")
            return True
    except Exception as e:
        print(f"Error reading robots.txt from {robots_url}: {e}")
        # If there's an error reading robots.txt, you might choose to proceed cautiously.
        return True

def fetch_initial_html(url):
    """
    Fetches the raw HTML using requests.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text, response.headers
    except Exception as e:
        print(f"Error fetching {url} with requests: {e}")
        return None, None

def fetch_rendered_html(url):
    """
    Uses Selenium to fetch the fully rendered HTML.
    """
    options = Options()
    options.headless = True
    # You might need to specify the path to your webdriver if it's not in PATH.
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        # Wait for the page to fully render. Adjust sleep time as necessary.
        time.sleep(5)
        rendered_html = driver.page_source
        return rendered_html
    except Exception as e:
        print(f"Error fetching rendered HTML with Selenium: {e}")
        return None
    finally:
        driver.quit()

def analyze_meta_robots(html):
    """
    Looks for meta robots tags in the HTML.
    """
    soup = BeautifulSoup(html, 'html.parser')
    meta_robots = soup.find_all("meta", attrs={"name": "robots"})
    if meta_robots:
        for meta in meta_robots:
            content = meta.get("content", "")
            print(f"Meta robots tag found: {content}")
    else:
        print("No meta robots tags found in HTML.")

def analyze_frameworks(html):
    """
    Scans the HTML (both full text and script tags) for hints of popular JS frameworks.
    """
    js_frameworks = {
        "React": ["react", "data-reactroot", "data-reactid"],
        "Angular": ["angular", "ng-app", "ng-controller"],
        "Vue": ["vue", "v-bind", "v-model"],
        "Ember": ["ember", "data-ember-action"],
    }

    detected_frameworks = set()
    lower_html = html.lower()

    # Check the entire HTML for framework keywords
    for framework, indicators in js_frameworks.items():
        for indicator in indicators:
            if indicator.lower() in lower_html:
                detected_frameworks.add(framework)
                break  # No need to check other indicators for this framework

    # Additionally, check within script tags for framework keywords in the src attributes.
    soup = BeautifulSoup(html, 'html.parser')
    script_tags = soup.find_all("script")
    for script in script_tags:
        src = script.get("src", "").lower()
        for framework, indicators in js_frameworks.items():
            for indicator in indicators:
                if indicator.lower() in src:
                    detected_frameworks.add(framework)
                    break

    if detected_frameworks:
        print(f"Detected JavaScript frameworks: {list(detected_frameworks)}")
    else:
        print("No obvious JavaScript frameworks detected.")
    return detected_frameworks

def analyze_page(url):
    """
    Main function that ties together all the heuristics.
    """
    print(f"Analyzing URL: {url}\n")
    # Step 1: Check robots.txt for scraping permissions
    if not check_robots(url):
        return

    # Step 2: Fetch raw HTML and headers
    print("\nFetching initial HTML...")
    raw_html, headers = fetch_initial_html(url)
    if not raw_html:
        return

    # Step 3: Check for meta robots tags in the raw HTML
    print("\nChecking for meta robots tags in raw HTML:")
    analyze_meta_robots(raw_html)

    # Step 4: Analyze for client-side frameworks in raw HTML
    print("\nAnalyzing frameworks in raw HTML...")
    frameworks_raw = analyze_frameworks(raw_html)

    # Step 5: Measure visible text in raw HTML
    soup_raw = BeautifulSoup(raw_html, 'html.parser')
    visible_text_raw = soup_raw.get_text(strip=True)
    len_raw = len(visible_text_raw)
    print(f"Visible text length (raw): {len_raw}")

    # Step 6: Fetch rendered HTML using Selenium
    print("\nFetching rendered HTML using Selenium...")
    rendered_html = fetch_rendered_html(url)
    if rendered_html:
        soup_rendered = BeautifulSoup(rendered_html, 'html.parser')
        visible_text_rendered = soup_rendered.get_text(strip=True)
        len_rendered = len(visible_text_rendered)
        print(f"Visible text length (rendered): {len_rendered}")

        # Compare the raw and rendered visible text lengths
        if len_raw == 0:
            ratio = float('inf')
        else:
            ratio = len_rendered / len_raw
        print(f"Rendered/Raw visible text length ratio: {ratio:.2f}")

        if ratio > 1.2:  # Adjust threshold as needed
            print("\nSignificant difference detected between raw and rendered HTML.")
            print("Recommendation: The site likely relies on JavaScript for loading content. Consider using a headless browser.")
        else:
            print("\nThe content difference between raw and rendered HTML is minimal.")
            print("Recommendation: Static scraping (using requests + BeautifulSoup) might be sufficient.")
    else:
        print("\nCould not fetch rendered HTML. Relying on raw HTML analysis.")
        print("Recommendation: Further manual inspection may be required.")

    # Step 7: Check for X-Robots-Tag header if present
    if headers:
        x_robots = headers.get("X-Robots-Tag")
        if x_robots:
            print(f"\nX-Robots-Tag header found: {x_robots}")

if __name__ == '__main__':
    url = input("Enter the URL to analyze: ").strip()
    analyze_page(url)
