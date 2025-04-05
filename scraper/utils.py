from .models import CustomUser

def get_or_create_user_instance(user_data):
    """
    Fetch the CustomUser instance from the database or create it if missing.
    """
    if not user_data or not user_data.get("email"):
        return None  # Ensure valid data exists

    user, created = CustomUser.objects.get_or_create(
        email=user_data["email"],
        defaults={
            "first_name": user_data.get("first_name", ""),
            "last_name": user_data.get("last_name", "")
        }
    )
    return user


# from django.core.mail import send_mail
# from django.conf import settings
# from django.db import connection

# def notify_price_drop():
#     with connection.cursor() as cursor:
#         # Get product details and user emails where the price has dropped
#         cursor.execute("""
#             SELECT u.email, p.title, p.current_price, t.target_price
#             FROM scraper_trackedproduct t
#             JOIN scraper_product p ON t.product_id = p.id
#             JOIN scraper_customuser u ON t.user_id = u.id
#             WHERE p.current_price <= t.target_price;
#         """)
#         rows = cursor.fetchall()

#         for email, title, current_price, target_price in rows:
#             subject = f"Price Drop Alert: {title}"
#             message = f"The price for '{title}' has dropped to {current_price} (target was {target_price})."
#             from_email = settings.DEFAULT_FROM_EMAIL
#             recipient_list = [email]

#             # Print email details for debugging
#             print(f"Sending email to: {email}")
#             print(f"Subject: {subject}")
#             print(f"Message: {message}")

#             # Send email
#             send_mail(subject, message, from_email, recipient_list)
#             print(f"Notification sent to {email}")

