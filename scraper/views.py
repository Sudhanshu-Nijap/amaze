from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal, InvalidOperation
import re
import json
import logging

from scraper.models import CustomUser, Bestseller, TodayDeals, Product, TrackedProduct, PriceHistory
from .bestseller import scrape_amazon_bestsellers
from .scraper import amazon_scraper
from .today_deals import scrape_amazon_today_offers
from django_celery_beat.models import PeriodicTask, CrontabSchedule

logger = logging.getLogger(__name__)

def home(request):
    """Render homepage with user details, bestsellers from DB, and today's deals."""
    user = request.user if request.user.is_authenticated else None

    # Fetch bestsellers from the database (latest 8)
    bestsellers = Bestseller.objects.order_by("-id")[:8]

    # Fetch today's deals (scraped live)
    today_deals = TodayDeals.objects.order_by("-id")[:8]

    return render(request, "frontpage.html", {
        "title": "amaze",
        "user": user,
        "products": bestsellers,  # Bestseller products from DB
        "products_deal": today_deals,  # Today's deals (scraped)
    })


def register_view(request):
    """Handles User Registration via Supabase Auth."""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        # 1. Attempt to Sign Up in Supabase
        from .supabase_client import supabase
        try:
            supabase_response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "first_name": first_name,
                        "last_name": last_name
                    }
                }
            })
            
            # Check if user already exists in Supabase
            if not supabase_response.user and not supabase_response.session:
                 pass 

        except Exception as e:
            # Supabase failed (e.g. user already exists, weak password, connection error)
            print(f"Supabase Registration Exception: {e}")
            error_msg = str(e)
            if "For security purposes, you can only request this after" in error_msg:
                error_msg = "Please wait a few seconds before trying again."
            elif "email rate limit exceeded" in error_msg.lower():
                error_msg = "Too many registration attempts. Please wait a while before trying again."
            return render(request, "register.html", {"error": f"Registration failed: {error_msg}"})

        # 2. Checks if local user exists, if not create one.
        if CustomUser.objects.filter(email=email).exists():
             return render(request, "register.html", {"error": "Email already registered."})

        try:
            # Create local user WITHOUT password
            user = CustomUser.objects.create_user(
                email=email,
                password=None, # No password stored locally
                first_name=first_name,
                last_name=last_name
            )
            user.set_unusable_password()
            user.save()
            
            # Log the user in locally using Django's backend
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            return redirect("home")

        except Exception as e:
            return render(request, "register.html", {"error": f"Local Error: {str(e)}"})

    return render(request, "register.html")


def login_view(request):
    """Handles User Login with Supabase Auth"""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # 1. Authenticate with Supabase
        from .supabase_client import supabase
        try:
            print(f"Attempting Supabase login for {email}")
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            # If successful, we get a user and session
            supabase_user = response.user
            print(f"Supabase login successful. User ID: {supabase_user.id if supabase_user else 'None'}")
            
            if supabase_user:
                # 2. Get or Create Local User (to maintain FKs)
                try:
                    user = CustomUser.objects.get(email=email)
                except CustomUser.DoesNotExist:
                     print("Creating local shadow user")
                     user = CustomUser.objects.create_user(
                        email=email,
                        password=None,
                        first_name=supabase_user.user_metadata.get('first_name', ''),
                        last_name=supabase_user.user_metadata.get('last_name', '')
                     )
                     user.set_unusable_password()
                     user.save()

                # 3. Create Django Session manually
                print("Logging in via Django backend")
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                # Check for next parameter
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect("tracked_products")
                
        except Exception as e:
            print(f"Login Exception: {e}")
            return render(request, "login.html", {"error": f"Login Failed: {str(e)}"})

    return render(request, "login.html")


def google_login(request):
    """Google Login is currently disabled."""
    return redirect("login_view")


def google_callback(request):
    """Google Login is currently disabled."""
    return redirect("login_view")


def logout_view(request):
    """Logs out user from Django and Supabase"""
    try:
        from .supabase_client import supabase
        supabase.auth.sign_out()
    except Exception as e:
        print(f"Supabase Logout Error: {e}")
        
    logout(request)
    return redirect("home")


@login_required(login_url="login_view")
def amazon_product_view(request):
    """Only logged-in users can track products"""
    user = request.user
    if request.method == "POST":
        user_input = request.POST.get("url")

        # Validate ASIN or URL
        asin_pattern = re.compile(r"^[A-Z0-9]{10}$")
        url = f"https://www.amazon.in/dp/{user_input}" if asin_pattern.match(user_input) else user_input

        try:
            product_data = amazon_scraper(url)
            if "error" in product_data:
                return render(request, "result.html", {"error_message": product_data["error"],"user": user})
            return render(request, "result.html", {"product": product_data,"user": user})
        except Exception as e:
            return render(request, "result.html", {"error_message": f"An error occurred: {e}","user": user})

    return render(request, "result.html", {"error_message": "Invalid request","user": user})


def bestsellers_view(request):
    """View to display Amazon Bestsellers from the database. If empty, scrape first."""
    user = request.user if request.user.is_authenticated else None
    start = int(request.GET.get("start", 0))  # Start index
    count = 20  # Number of products per page

    # Debugging: Check if products exist
    product_count = Bestseller.objects.count()
    print(f"Products in DB: {product_count}")  # Check if DB has products

    if product_count == 0:  # Only scrape if DB is empty
        print("Database empty. Scraping new products...")
        scraped_products = scrape_amazon_bestsellers(start=0, count=20)

        # Save scraped data efficiently using bulk_create
        Bestseller.objects.bulk_create([
            Bestseller(
                title=product["title"],
                current_price=product["current_price"],
                image_url=product["image_url"],
                product_url=product["product_url"]
            ) for product in scraped_products
        ])
        print("Scraped data saved.")

    # Fetch products from DB
    products = Bestseller.objects.all().order_by("-scraped_at")[start : start + count]

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":  # AJAX Request
        return JsonResponse({
            "products": list(products.values("title", "current_price", "image_url", "product_url")),
            "start": start,
            "count": count,
        })
    
    return render(request, "bestseller.html", {
        "user": user,
        "products": products,
        "start": start,
        "count": count,
    })


def today_view(request):
    """View to display Amazon Today's Deals from the database. If empty, scrape first."""
    user = request.user if request.user.is_authenticated else None
    start = int(request.GET.get("start", 0))  # Start index
    count = 20  # Number of products per page

    # Debugging: Check if products exist
    product_count = TodayDeals.objects.count()
    print(f"Today's Deals in DB: {product_count}")  # Check if DB has products

    if product_count == 0:  # Only scrape if DB is empty
        print("Database empty. Scraping new Today's Deals...")
        scraped_products = scrape_amazon_today_offers(start=0, count=20)

        # Save scraped data efficiently using bulk_create
        TodayDeals.objects.bulk_create([
            TodayDeals(
                title=product["title"],
                current_price=product["current_price"],
                image_url=product["image"],
                product_url=product["url"]
            ) for product in scraped_products
        ])
        print("Scraped Today's Deals saved.")

    # Fetch products from DB
    product_deal = TodayDeals.objects.all().order_by("-scraped_at")[start : start + count]

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":  # AJAX Request
        return JsonResponse({
            "product_deal": list(product_deal.values("title", "current_price", "image_url", "product_url")),
            "start": start,
            "count": count,
        })
    
    return render(request, "today.html", {
        "user": user,
        "product_deal": product_deal,
        "start": start,
        "count": count,
    })

@login_required(login_url="login_view")
def result(request):
    """Fetch product details from DB if available; otherwise, scrape them."""
    user = request.user
    url = request.GET.get("url")

    if not url:
        return render(request, "result.html", {"error_message": "Invalid request. No product URL provided.", "user": user})

    try:
        product = Product.objects.filter(amazon_url=url).first()
        product_from_db = bool(product)
        price_history = []

        if product:
            product_data = {
                'asin': product.asin,
                "title": product.title,
                "image_url": product.image_url,
                "current_price": product.current_price or 0,  # Ensure no None value
                "rating": product.rating,
                "stock_status": product.stock_status,
                "amazon_url": product.amazon_url,
            }

            # Fetch price history sorted by date (ascending)
            price_history_qs = PriceHistory.objects.filter(product=product).order_by("timestamp")
            price_history = [
                {"date": ph.timestamp.strftime("%Y-%m-%d"), "price": ph.price} for ph in price_history_qs
            ]

        else:
            product_data = amazon_scraper(url)
            if not product_data or "error" in product_data:
                return render(request, "result.html", {"error_message": product_data.get("error", "Failed to fetch product."), "user": user})

        return render(
            request,
            "result.html",
            {
                "product": product_data,
                "product_from_db": product_from_db,
                "price_history": price_history,
                "user": user,
            }
        )

    except Exception as e:
        return render(request, "result.html", {"error_message": f"An error occurred: {e}", "user": user})


@login_required(login_url="login_view")
def tracked_products_view(request):
    """Display products tracked by the logged-in user."""
    user = request.user

    # Fetch tracked products with related product details
    tracked_products = TrackedProduct.objects.filter(user=user).select_related("product")

    return render(request, "tracked_products.html", {
        "user": user,  # Pass the user object directly to the template
        "tracked_products": tracked_products
    })


@csrf_exempt
def track_products_db(request):
    """API to track a product for a user."""
    if request.method == "POST":
        try:
            # Check authentication
            if not request.user.is_authenticated:
                 return JsonResponse({"error": "User not authenticated."}, status=401)
            
            user = request.user

            data = json.loads(request.body)
            asin = data.get("asin")
            desired_price = data.get("desired_price")
            current_price = data.get("current_price")

            if not asin:
                return JsonResponse({"error": "ASIN is required."}, status=400)

            # Convert price to Decimal
            try:
                desired_price = Decimal(str(desired_price).replace(",", "").strip()) or 0
                current_price = Decimal(str(current_price).replace(",", "").strip()) or 0
                if desired_price <= 0:
                    return JsonResponse({"error": "Invalid desired price."}, status=400)
            except InvalidOperation:
                return JsonResponse({"error": "Invalid price format."}, status=400)

            # Check if product exists in Supabase (or insert if new)
            product, created = Product.objects.get_or_create(
                asin=asin,
                defaults={
                    "title": data.get("title"),
                    "image_url": data.get("image_url"),
                    "current_price": current_price,
                    "rating": data.get("rating", "0 out of 5 stars"),
                    "stock_status": data.get("stock_status"),
                    "amazon_url": data.get("amazon_url"),
                }
            )

            # Update the current price if it has changed
            if not created and product.current_price != current_price:
                product.current_price = current_price
                product.save()

            # Add product to TrackedProduct
            tracked_product, created = TrackedProduct.objects.get_or_create(
                user=user,
                product=product,
                defaults={"target_price": desired_price}
            )

            if not created:
                # Update the target price if it has changed
                if tracked_product.target_price != desired_price:
                    tracked_product.target_price = desired_price
                    tracked_product.save()

            # **Save Price History**
            PriceHistory.objects.create(user=user, product=product, price=desired_price)

            return JsonResponse({"success": True})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def remove_product_db(request, asin):
    """Removes a product from the user's tracked products."""
    if request.method != "DELETE":
        return JsonResponse({"error": "Invalid request method. Only DELETE is allowed."}, status=405)

    # Authenticate User
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated."}, status=401)
    
    user = request.user

    # Delete TrackedProduct
    try:
        tracked_product = get_object_or_404(TrackedProduct, user=user, product__asin=asin)
        tracked_product.delete()
        return JsonResponse({
            "success": True,
            "message": "✅ Product removed successfully from your Price Watch."
        })
    except Exception as e:
        return JsonResponse({"error": f"❌ Failed to delete product. {str(e)}"}, status=500)


def schedule_mail(request):
    """Schedule `notify_price_drop` task to run every 4 minutes."""
    
    # Create a crontab schedule (Runs every 4 minutes)
    schedule, created = CrontabSchedule.objects.get_or_create(
        minute='*/4', hour='*', day_of_week='*', day_of_month='*', month_of_year='*'
    )

    # Create or update the periodic task
    task, created = PeriodicTask.objects.update_or_create(
        name="price_drop_notification_task",
        defaults={
            'crontab': schedule,
            'task': 'scraper.tasks.notify_price_drop',  # Ensure the path is correct
            'args': json.dumps([]),  # No arguments needed
            'enabled': True,
        }
    )

    if created:
        logger.info("Scheduled price drop email task every 4 minutes.")
    else:
        logger.info("Updated existing price drop email task.")

    return JsonResponse({"message": "Task scheduled successfully!", "created": created})

def schedule_bestsellers(request):
    """Schedule `bestsellers_task` to run every 4 minutes."""
    # Create a crontab schedule (for every 4 minutes)
    schedule, created = CrontabSchedule.objects.get_or_create(
        minute='*/4', hour='*', day_of_week='*', day_of_month='*', month_of_year='*'
    )

    # Create a periodic task
    task, created = PeriodicTask.objects.update_or_create(
        name="bestsellers_task",
        defaults={
            'crontab': schedule,
            'task': 'scraper.tasks.bestsellers_task',  # Ensure correct task path
            'args': json.dumps([]),  # Arguments if needed
        }
    )

    if created:
        print("Scheduled periodic task successfully!")
    else:
        print("Updated existing task.")
    return JsonResponse({"message": "Task scheduled successfully!", "created": created})


def schedule_today_offers(request):
    """Schedule `today_offers_task` to run every 4 minutes."""
    # Create a crontab schedule (for every 4 minutes)
    schedule, created = CrontabSchedule.objects.get_or_create(
        minute='*/4', hour='*', day_of_week='*', day_of_month='*', month_of_year='*'
    )

    # Create a periodic task
    task, created = PeriodicTask.objects.update_or_create(
        name="today_offers_task",
        defaults={
            'crontab': schedule,
            'task': 'scraper.tasks.today_offers_task',  # Ensure correct task path
            'args': json.dumps([]),  # Arguments if needed
        }
    )

    if created:
        print("Scheduled periodic task successfully!")
    else:
        print("Updated existing task.")
    return JsonResponse({"message": "Task scheduled successfully!", "created": created})




