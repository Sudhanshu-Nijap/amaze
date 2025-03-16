from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re

# ScraperAPI Key
SCRAPERAPI_KEY = "67cda07a9b699640ce78da5d0b275e99"

def get_scraperapi_url(url):
    return f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}"

def extract_asin(url):
    match = re.search(r"(?:dp|gp/product)/([A-Z0-9]{10})", url)
    return match.group(1) if match else None

def amazon_scraper(url):
    try:
        scraperapi_url = get_scraperapi_url(url)

        # Set up Selenium options for headless browsing
        options = Options()
        options.add_argument('--headless')

        driver = webdriver.Chrome(options=options)
        driver.get(scraperapi_url)

        # Wait for JavaScript to load
        time.sleep(5)

        # Get the page source after JavaScript content has been rendered
        html_source = driver.page_source

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(html_source, "html.parser")

        # Extract ASIN from URL
        asin = extract_asin(url)

        # Extract product title
        title = soup.find("span", {"id": "productTitle"})
        title = title.get_text(strip=True) if title else "No title found"

        # Extract product price
        price = soup.find("span", class_="a-price-whole")
        price = price.get_text(strip=True) if price else "Price not available"

        # Extract product rating
        rating = soup.find("span", {"class": "a-icon-alt"})
        rating = rating.get_text(strip=True) if rating else "Rating not available"

        # Extract the product image URL
        image_url = soup.find("img", {"id": "landingImage"})
        image_url = image_url['src'] if image_url else "Image URL not available"

        # Initialize product info dictionary
        product_info = {}

        # Case 1: Try extracting from "productDetails_techSpec_section_1"
        product_info_table = soup.find("table", {"id": "productDetails_techSpec_section_1"})
        if product_info_table:
            rows = product_info_table.find_all("tr")
            for row in rows:
                key = row.find("th").get_text(strip=True)
                value = row.find("td").get_text(strip=True)
                product_info[key] = re.sub(r'\u200e', '', value)

        # Case 2: If Case 1 fails, extract from "detailBullets_feature_div"
        if not product_info: 
            detail_bullets = soup.find("div", {"id": "detailBullets_feature_div"})
            if detail_bullets:
                items = detail_bullets.find_all("span", class_="a-list-item")
                for item in items:
                    text = item.get_text(strip=True).split(":", 1)  # Split key-value pairs
                    if len(text) == 2:
                        key, value = text
                        product_info[key.strip()] = value.strip()

        # Check stock availability
        stock_status = soup.find("input", {"id": "add-to-cart-button"}) is not None

        # Close Selenium driver
        driver.quit()

        return {
            "asin": asin,
            "title": title,
            "current_price": price,
            "rating": rating,
            "image_url": image_url,
            "product_info": product_info,
            "stock_status": stock_status,
            "url": url
        }

    except Exception as e:
        return {"error": f"An error occurred: {e}"}
