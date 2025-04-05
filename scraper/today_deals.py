import re
import requests
from bs4 import BeautifulSoup
from decimal import Decimal
from urllib.parse import urlparse, urlunparse
from .models import TodayDeals  # Import TodayDeals model

SCRAPERAPI_KEY = "16830b77d12c2f914cba166d5291c960"

def get_scraperapi_url(url):
    """Returns the ScraperAPI proxy URL."""
    return f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}&render=true"

def clean_price(price_str):
    """Removes currency symbols and commas, then converts to Decimal."""
    cleaned_price = re.sub(r"[^\d.]", "", price_str)
    return Decimal(cleaned_price) if cleaned_price else None

def normalize_url(url):
    """Removes tracking parameters from the Amazon URL to avoid duplicates."""
    parsed_url = urlparse(url)
    clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", "", ""))
    return clean_url

def scrape_amazon_today_offers(start=0, count=8):
    """Scrapes Amazon Today's Deals, saves them to DB, and returns a limited number of products."""
    
    url = "https://www.amazon.in/s?k=today+offer"
    scraperapi_url = get_scraperapi_url(url)

    try:
        response = requests.get(scraperapi_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []  # Return empty list if request fails

    soup = BeautifulSoup(response.text, "html.parser")

    products = soup.find_all("div", {"data-component-type": "s-search-result"})

    extracted_products = []
    for product in products:
        title_tag = product.find("h2").find("span") if product.find("h2") else None
        title = title_tag.text.strip() if title_tag else "No title found"

        price_tag = product.find("span", class_="a-price-whole")
        price = clean_price(price_tag.get_text(strip=True)) if price_tag else None

        img_tag = product.find("img", class_="s-image")
        img_url = img_tag["src"] if img_tag else None

        link_tag = product.find("a", class_="a-link-normal")
        product_url = normalize_url("https://www.amazon.in" + link_tag["href"]) if link_tag else None

        if img_url and product_url and title and price is not None:
            # Save to DB if not already exists
            today_deal, created = TodayDeals.objects.update_or_create(
                product_url=product_url,
                defaults={"title": title, "current_price": price, "image_url": img_url}
            )
            
            extracted_products.append({
                "title": today_deal.title,
                "current_price": str(today_deal.current_price),  # Convert to string for JSON serialization
                "image_url": today_deal.image_url,
                "product_url": today_deal.product_url
            })

    return extracted_products[start : start + count]
