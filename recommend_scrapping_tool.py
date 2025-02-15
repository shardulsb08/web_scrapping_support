# recommend_scrapping_tool.py

import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import sys

# Import Selenium functionality from our helper module
from selenium_utils import fetch_rendered_html

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
            print(f"Scraping disallowed by robots.txt at {robots_url}", flush=True)
            return False
        else:
            print(f"Scraping allowed by robots.txt at {robots_url}", flush=True)
            return True
    except Exception as e:
        print(f"Error reading robots.txt from {robots_url}: {e}", flush=True)
        # Assume allowed if there's an error reading robots.txt.
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
        print(f"Error fetching {url} with requests: {e}", flush=True)
        return None, None

def analyze_meta_robots(html):
    """
    Looks for meta robots tags in the HTML.
    """
    soup = BeautifulSoup(html, 'html.parser')
    meta_robots = soup.find_all("meta", attrs={"name": "robots"})
    if meta_robots:
        for meta in meta_robots:
            content = meta.get("content", "")
            print(f"Meta robots tag found: {content}", flush=True)
    else:
        print("No meta robots tags found in HTML.", flush=True)

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

    # Check the entire HTML for framework keywords.
    for framework, indicators in js_frameworks.items():
        for indicator in indicators:
            if indicator.lower() in lower_html:
                detected_frameworks.add(framework)
                break

    # Also check within <script> tags for keywords.
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup.find_all("script"):
        src = script.get("src", "").lower()
        for framework, indicators in js_frameworks.items():
            for indicator in indicators:
                if indicator.lower() in src:
                    detected_frameworks.add(framework)
                    break

    if detected_frameworks:
        print(f"Detected JavaScript frameworks: {list(detected_frameworks)}", flush=True)
    else:
        print("No obvious JavaScript frameworks detected.", flush=True)
    return detected_frameworks

def analyze_page(url):
    print(f"Analyzing URL: {url}\n", flush=True)

    # 1. Check robots.txt
    if not check_robots(url):
        return

    # 2. Fetch raw HTML and headers.
    print("\nFetching initial HTML...", flush=True)
    raw_html, headers = fetch_initial_html(url)
    if not raw_html:
        return

    # 3. Check for meta robots tags.
    print("\nChecking for meta robots tags in raw HTML:", flush=True)
    analyze_meta_robots(raw_html)

    # 4. Analyze frameworks in raw HTML.
    print("\nAnalyzing frameworks in raw HTML...", flush=True)
    analyze_frameworks(raw_html)

    # 5. Measure visible text in raw HTML.
    soup_raw = BeautifulSoup(raw_html, 'html.parser')
    visible_text_raw = soup_raw.get_text(strip=True)
    len_raw = len(visible_text_raw)
    print(f"Visible text length (raw): {len_raw}", flush=True)

    # 6. Fetch rendered HTML using Selenium.
    print("\nFetching rendered HTML using Selenium...", flush=True)
    rendered_html = fetch_rendered_html(url)
    if rendered_html:
        soup_rendered = BeautifulSoup(rendered_html, 'html.parser')
        visible_text_rendered = soup_rendered.get_text(strip=True)
        len_rendered = len(visible_text_rendered)
        print(f"Visible text length (rendered): {len_rendered}", flush=True)

        # Compare raw and rendered content.
        ratio = float('inf') if len_raw == 0 else len_rendered / len_raw
        print(f"Rendered/Raw visible text length ratio: {ratio:.2f}", flush=True)

        if ratio > 1.2:  # Adjust threshold as needed.
            print("\nSignificant difference detected between raw and rendered HTML.", flush=True)
            print("Recommendation: The site likely relies on JavaScript for loading content. Consider using a headless browser.", flush=True)
        else:
            print("\nThe content difference between raw and rendered HTML is minimal.", flush=True)
            print("Recommendation: Static scraping (using requests + BeautifulSoup) might be sufficient.", flush=True)
    else:
        print("\nCould not fetch rendered HTML. Relying on raw HTML analysis.", flush=True)
        print("Recommendation: Further manual inspection may be required.", flush=True)

    # 7. Check for X-Robots-Tag header.
    if headers:
        x_robots = headers.get("X-Robots-Tag")
        if x_robots:
            print(f"\nX-Robots-Tag header found: {x_robots}", flush=True)

if __name__ == '__main__':
    # If a URL argument is provided, use it; otherwise, prompt for input.
    if len(sys.argv) > 1:
        url = sys.argv[1].strip()
    else:
        url = input("Enter the URL to analyze: ").strip()
    analyze_page(url)
