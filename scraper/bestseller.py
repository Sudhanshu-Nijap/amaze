# import re
# import requests
# from bs4 import BeautifulSoup
# from decimal import Decimal
# from urllib.parse import urlparse, urlunparse
# from .models import Bestseller  

# SCRAPERAPI_KEY = "16830b77d12c2f914cba166d5291c960"

# def get_scraperapi_url(url):
#     """Returns the ScraperAPI proxy URL."""
#     return f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}&render=true"

# def clean_price(price_str):
#     """Removes currency symbols and commas, then converts to Decimal."""
#     cleaned_price = re.sub(r"[^\d.]", "", price_str)
#     return Decimal(cleaned_price) if cleaned_price else None

# def normalize_url(url):
#     """Removes tracking parameters from the Amazon URL to avoid duplicates."""
#     parsed_url = urlparse(url)
#     clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", "", ""))
#     return clean_url

# def scrape_amazon_bestsellers(start=0, count=8):
#     """Scrapes Amazon Bestsellers, saves them to DB, and returns the products."""
    
#     url = "https://www.amazon.in/gp/bestsellers/"
#     scraperapi_url = get_scraperapi_url(url)

#     response = requests.get(scraperapi_url)

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, "html.parser")
#         products = soup.find_all("div", class_="p13n-sc-uncoverable-faceout")  

#         extracted_products = []
#         for product in products:
#             title_tag = product.find("div", class_="p13n-sc-truncate") or product.find("span", class_="a-size-medium")
#             title = title_tag.text.strip() if title_tag else "No title found"

#             price_tag = product.find("span", class_="_cDEzb_p13n-sc-price_3mJ9Z") or product.find("span", class_="a-price-whole")
#             price = clean_price(price_tag.get_text(strip=True)) if price_tag else None  # Convert price properly

#             img_tag = product.find("img")
#             img_url = img_tag["src"] if img_tag else None

#             link_tag = product.find("a", class_="a-link-normal")
#             product_url = normalize_url("https://www.amazon.in" + link_tag["href"]) if link_tag else None  # Normalize URL

#             if img_url and product_url and title and price is not None:
#                 # Save to DB if not already exists
#                 bestseller, created = Bestseller.objects.update_or_create(
#                     product_url=product_url,
#                     defaults={"title": title, "current_price": price, "image_url": img_url}
#                 )
#                 extracted_products.append({"title": bestseller.title, "current_price": str(bestseller.current_price), "image_url": bestseller.image_url, "product_url": bestseller.product_url})

#         return extracted_products[start : start + count]  

#     return []

import requests
import re
from bs4 import BeautifulSoup
from decimal import Decimal
from urllib.parse import urlparse, urlunparse, urlencode
from .models import Bestseller  

SCRAPERAPI_KEY = "16830b77d12c2f914cba166d5291c960"
AFFILIATE_TAG = "your-affiliate-id"  # Replace with your Amazon affiliate ID

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

def add_affiliate_tag(url):
    """Appends the Amazon affiliate tag to the product URL."""
    parsed_url = urlparse(url)
    query_params = {"tag": AFFILIATE_TAG}  # Add affiliate tag
    affiliate_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", urlencode(query_params), ""))
    return affiliate_url

def scrape_amazon_bestsellers(start=0, count=8):
    """Scrapes Amazon Bestsellers, saves them to DB, and returns the products."""
    
    url = "https://www.amazon.in/gp/bestsellers/"
    scraperapi_url = get_scraperapi_url(url)

    response = requests.get(scraperapi_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        products = soup.find_all("div", class_="p13n-sc-uncoverable-faceout")  

        extracted_products = []
        for product in products:
            title_tag = product.find("div", class_="p13n-sc-truncate") or product.find("span", class_="a-size-medium")
            title = title_tag.text.strip() if title_tag else "No title found"

            price_tag = product.find("span", class_="_cDEzb_p13n-sc-price_3mJ9Z") or product.find("span", class_="a-price-whole")
            price = clean_price(price_tag.get_text(strip=True)) if price_tag else None  # Convert price properly

            img_tag = product.find("img")
            img_url = img_tag["src"] if img_tag else None

            link_tag = product.find("a", class_="a-link-normal")
            product_url = normalize_url("https://www.amazon.in" + link_tag["href"]) if link_tag else None  # Normalize URL

            if product_url:
                product_url = add_affiliate_tag(product_url)  # Convert to affiliate link

            if img_url and product_url and title and price is not None:
                # Save to DB if not already exists
                bestseller, created = Bestseller.objects.update_or_create(
                    product_url=product_url,
                    defaults={"title": title, "current_price": price, "image_url": img_url}
                )
                extracted_products.append({
                    "title": bestseller.title,
                    "current_price": str(bestseller.current_price),
                    "image_url": bestseller.image_url,
                    "product_url": bestseller.product_url
                })

        return extracted_products[start : start + count]  

    return []
