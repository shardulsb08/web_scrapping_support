import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

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
        # Here "*" represents any user-agent; modify if needed.
        if not rp.can_fetch("*", url):
            print(f"Scraping disallowed by robots.txt at {robots_url}")
            return False
        else:
            print(f"Scraping allowed by robots.txt at {robots_url}")
            return True
    except Exception as e:
        print(f"Error reading robots.txt from {robots_url}: {e}")
        # If there's an error reading robots.txt, you may choose to proceed or not.
        # For now, we'll assume allowed.
        return True

def analyze_page(url):
    # First, check robots.txt
    if not check_robots(url):
        return

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return

    # Heuristic indicators for client-side rendering frameworks
    js_frameworks = {
        "React": ["data-reactroot", "data-reactid", "react"],
        "Angular": ["ng-app", "ng-controller", "angular"],
        "Vue": ["vue", "v-bind", "v-model"],
        "Ember": ["ember", "data-ember-action"],
    }

    detected_frameworks = []
    lower_html = html.lower()
    for framework, indicators in js_frameworks.items():
        if any(indicator.lower() in lower_html for indicator in indicators):
            detected_frameworks.append(framework)

    if detected_frameworks:
        print(f"Detected JavaScript frameworks: {detected_frameworks}")
        print("Recommendation: Consider using a headless browser (e.g., Selenium or Puppeteer) to fully render the page.")
    else:
        # Further analysis: Check if there's substantial visible text in the initial HTML.
        soup = BeautifulSoup(html, 'html.parser')
        visible_text = soup.get_text(strip=True)
        if len(visible_text) < 100:
            print("The initial HTML appears to have minimal content.")
            print("Recommendation: The site might load content dynamically. A headless browser could be necessary.")
        else:
            print("No heavy client-side frameworks detected and the page contains substantial content.")
            print("Recommendation: Static scraping (using requests + BeautifulSoup) might be sufficient.")

if __name__ == '__main__':
    url = input("Enter the URL to analyze: ").strip()
    analyze_page(url)
