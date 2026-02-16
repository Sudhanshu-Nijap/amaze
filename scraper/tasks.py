import logging
from django.core.mail import send_mass_mail
from django.conf import settings
from django.db import connection
from celery import shared_task

# Set up logging
logger = logging.getLogger(__name__)

@shared_task  # Removed bind=True (not needed)
def notify_price_drop():
    """
    Celery task to check for price drops and send email notifications.
    Queries the database for products where current_price <= target_price.
    """
    logger.info("Starting notify_price_drop task...")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.email, p.title, p.current_price, t.target_price
            FROM scraper_trackedproduct t
            JOIN scraper_product p ON t.product_id = p.id
            JOIN scraper_customuser u ON t.user_id = u.id
            WHERE p.current_price <= t.target_price;
        """)
        rows = cursor.fetchall()
    logger.info(f"Fetched rows: {rows}")

    if not rows:
        logger.info("No price drops found.")
        return "No price drops."

    messages = []
    for email, title, current_price, target_price in rows:
        subject = f"Price Drop Alert: {title}"
        message = f"The price for '{title}' has dropped to {current_price} (target was {target_price})."
        from_email = settings.DEFAULT_FROM_EMAIL
        messages.append((subject, message, from_email, [email]))
        logger.info(f"Prepared email for {email} | {title} | {current_price}")

    try:
        logger.info(f"Sending {len(messages)} emails...")
        send_mass_mail(messages, fail_silently=False)  
        logger.info("Emails sent successfully.")
        return f"Sent {len(messages)} price drop notifications."
    except Exception as e:
        logger.error(f"Error sending emails: {str(e)}")
        return str(e)
    

from .bestseller import scrape_amazon_bestsellers  
from .today_deals import scrape_amazon_today_offers  

@shared_task
def bestsellers_task():
    """Celery task to scrape Amazon Bestsellers."""
    return scrape_amazon_bestsellers()

@shared_task
def today_offers_task():
    """Celery task to scrape Amazon Today's Deals."""
    return scrape_amazon_today_offers()