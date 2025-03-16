from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from supabase import create_client
import re
from django.db import models

from .models import CustomUser  # Import your CustomUser model


from .bestseller import scrape_amazon_bestsellers
from .scraper import amazon_scraper
from .today_deals import scrape_amazon_today_offers

# Initialize Supabase Client
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_current_user(request):
    """Fetch logged-in user from Supabase and ensure they exist in the Django DB."""
    token = request.COOKIES.get("supabase_token")  # Get token from cookie
    if not token:
        return None  

    try:
        user_response = supabase.auth.get_user(token)  # Fetch user from Supabase
        if user_response and user_response.user:
            user_data = user_response.user
            email = user_data.email
            first_name = user_data.user_metadata.get("first_name", "")
            last_name = user_data.user_metadata.get("last_name", "")
            avatar = user_data.user_metadata.get("avatar_url", "")

            # Ensure user exists in the Django database
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={"first_name": first_name, "last_name": last_name}
            )

            return {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "avatar": avatar
            }

    except Exception as e:
        print("Error fetching user:", e)
    
    return None


from django.shortcuts import render
from .models import Bestseller
# from .utils import get_current_user, scrape_amazon_today_offers  # Assuming utils contains these functions

def home(request):
    """Render homepage with user details, bestsellers from DB, and today's deals."""
    user = get_current_user(request)  # Fetch user from Supabase

    # Fetch bestsellers from the database (latest 8)
    bestsellers = Bestseller.objects.order_by("-id")[:8]

    # Fetch today's deals (scraped live)
    today_deals = TodayDeals.objects.order_by("-id")[:8]

    return render(request, "frontpage.html", {
        "user": user,
        "products": bestsellers,  # Bestseller products from DB
        "products_deal": today_deals,  # Today's deals (scraped)
    })



def register_view(request):
    """Handles User Registration with Supabase and stores in Django DB."""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {  # Store First & Last Name in Metadata
                        "first_name": first_name,
                        "last_name": last_name
                    }
                }
            })

            if response and response.user:
                # Also store the user in Django database
                CustomUser.objects.get_or_create(
                    email=email,
                    defaults={"first_name": first_name, "last_name": last_name}
                )
                
                return redirect("login_view")  # Redirect to login after signup
            else:
                return render(request, "register.html", {"error": "Registration failed. Try again."})

        except Exception as e:
            return render(request, "register.html", {"error": str(e)})

    return render(request, "register.html")


def login_view(request):
    """Handles User Login with Supabase"""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})

            if response and response.session:
                token = response.session.access_token  # Get token
                
                # Store token in HTTP-only cookie
                response_obj = redirect("home")  # Redirect after login
                response_obj.set_cookie("supabase_token", token, httponly=True)
                return response_obj

            else:
                return render(request, "login.html", {"error": "Invalid credentials"})

        except Exception as e:
            return render(request, "login.html", {"error": str(e)})

    return render(request, "login.html")


def google_login(request):
    """Redirects user to Supabase Google OAuth login"""
    google_auth_url = f"{settings.SUPABASE_URL}/auth/v1/authorize?provider=google&redirect_to={settings.SITE_URL}/callback"
    return redirect(google_auth_url)

def google_callback(request):
    """Handles Google OAuth callback and stores user session in DB."""
    access_token = request.GET.get("access_token")

    if not access_token:
        return redirect("login_view")  # If no token, go back to login

    try:
        # Fetch user details using Supabase API
        user_response = supabase.auth.get_user(access_token)

        if user_response and user_response.user:
            user_data = user_response.user
            email = user_data.email
            first_name = user_data.user_metadata.get("first_name", "")
            last_name = user_data.user_metadata.get("last_name", "")
            avatar = user_data.user_metadata.get("avatar_url", "")

            # Store user in Django DB if not exists
            CustomUser.objects.get_or_create(
                email=email,
                defaults={"first_name": first_name, "last_name": last_name}
            )

            # Store token in HTTP-only cookie
            response_obj = redirect("home")
            response_obj.set_cookie("supabase_token", access_token, httponly=True)

            return response_obj

    except Exception as e:
        print("Google Login Error:", e)
        return redirect("login_view")

    return redirect("login_view")


def logout_view(request):
    """Logs out user by clearing the Supabase token cookie"""
    response = redirect("login_view")
    response.delete_cookie("supabase_token")  # Remove token from cookies
    return response


def login_required_supabase(view_func):
    """Decorator to protect views for logged-in users via Supabase."""
    def wrapper(request, *args, **kwargs):
        if not get_current_user(request):
            return redirect("login_view")
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required_supabase
def amazon_product_view(request):
    """Only logged-in users can track products"""
    user = get_current_user(request)
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

# @login_required_supabase
# def bestsellers_view(request):
#     """View to display Amazon Bestsellers with AJAX pagination."""
#     user = get_current_user(request)
#     start = int(request.GET.get("start", 0))  # Start index
#     count = 20  # Number of products per page
    
#     products = scrape_amazon_bestsellers(start=start, count=count)

#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX Request
#         return JsonResponse({"products": products, "start": start, "count": count})
    
#     return render(request, "bestseller.html", {
#         "user": user,
#         "products": products,
#         "start": start,
#         "count": count,
#     })






from django.shortcuts import render
from django.http import JsonResponse
from .models import Bestseller
# from scraper.auth_utils import get_current_user
# from scraper.utils import scrape_amazon_bestsellers  # Import your scraper function

from django.db.models import Count

def bestsellers_view(request):
    """View to display Amazon Bestsellers from the database. If empty, scrape first."""
    user = get_current_user(request)
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




def load_more_products(request):
    try:
        start = int(request.GET.get("start", 0))  # Get start index for pagination
        count = 8  # Number of products to fetch each time
        
        # Fetch products based on the start and count
        products = scrape_amazon_bestsellers(start=start, count=count)
        
        # Return products in JSON response
        return JsonResponse({"products": products})
    
    except ValueError:
        return JsonResponse({"error": "Invalid start parameter"}, status=400) 




# @login_required_supabase
# def today_view(request):
#     """View to display Amazon Bestsellers with AJAX pagination."""
#     user = get_current_user(request)
#     start = int(request.GET.get("start", 0))  # Start index
#     count = 20  # Number of products per page
    
#     product_deal = scrape_amazon_today_offers(start=start, count=count)

#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX Request
#         return JsonResponse({"product_deal": product_deal, "start": start, "count": count})
    
#     return render(request, "today.html", {
#         "user": user,
#         "product_deal": product_deal,
#         "start": start,
#         "count": count,
#     })


from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from .models import TodayDeals
# from .scraper import scrape_amazon_today_offers
# from .auth_utils import get_current_user  # Assuming you have this function for authentication

def today_view(request):
    """View to display Amazon Today's Deals from the database. If empty, scrape first."""
    user = get_current_user(request)
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


def load_deal_products(request):
    try:
        start = int(request.GET.get("start", 0))  # Get start index for pagination
        count = 8  # Number of products to fetch each time
        
        # Fetch products based on the start and count
        products = scrape_amazon_today_offers(start=start, count=count)
        
        # Return products in JSON response
        return JsonResponse({"products": products})
    
    except ValueError:
        return JsonResponse({"error": "Invalid start parameter"}, status=400) 

# very old
# def result(request):
#     """Fetch product details from the clicked URL and display them."""
#     user = get_current_user(request)
#     url = request.GET.get("url")  # Get URL from the clicked product

#     if not url:
#         return render(request, "result.html", {"error_message": "Invalid request. No product URL provided.","user": user})

#     try:
#         product_data = amazon_scraper(url)  # Scrape product details

#         if "error" in product_data:
#             return render(request, "result.html", {"error_message": product_data["error"],"user": user})

#         return render(request, "result.html", {"product": product_data,"user": user})

#     except Exception as e:
#         return render(request, "result.html", {"error_message": f"An error occurred: {e}","user": user})
    









# old 
# def result(request):
#     """Fetch product details from DB if available; otherwise, scrape them."""
#     user = get_current_user(request)
#     url = request.GET.get("url")

#     if not url:
#         return render(request, "result.html", {"error_message": "Invalid request. No product URL provided.", "user": user})

#     try:
#         product = Product.objects.filter(amazon_url=url).first()
#         product_from_db = bool(product)  # Flag to indicate if product is from DB

#         if product:
#             product_data = {
#                 "title": product.title,
#                 "image_url": product.image_url,
#                 "current_price": product.current_price,
#                 "rating": product.rating,
#                 "stock_status": product.stock_status,
#                 "amazon_url": product.amazon_url,
#             }
#         else:
#             product_data = amazon_scraper(url)
#             if "error" in product_data:
#                 return render(request, "result.html", {"error_message": product_data["error"], "user": user})

#         return render(request, "result.html", {"product": product_data, "product_from_db": product_from_db, "user": user})

#     except Exception as e:
#         return render(request, "result.html", {"error_message": f"An error occurred: {e}", "user": user})

from django.shortcuts import render
import json

def result(request):
    """Fetch product details from DB if available; otherwise, scrape them."""
    user = get_current_user(request)
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
























from django.core.exceptions import ObjectDoesNotExist
from .models import TrackedProduct, CustomUser

@login_required_supabase
def tracked_products_view(request):
    """Display products tracked by the logged-in user."""
    user = get_current_user(request)  # Get user details from Supabase

    if not user or 'email' not in user:
        # Handle missing or invalid user data
        return render(request, "tracked_products.html", {"error_message": "User not found. Please log in again.","user": user})

    try:
        # Fetch the actual CustomUser instance using the email
        django_user = CustomUser.objects.get(email=user['email'])
    except ObjectDoesNotExist:
        return render(request, "tracked_products.html", {"error_message": "User not found. Please log in again."})

    # Fetch tracked products with related product details
    tracked_products = TrackedProduct.objects.filter(user=django_user).select_related("product")

    return render(request, "tracked_products.html", {
        "user": user,  # Pass the user object directly to the template
        "tracked_products": tracked_products
    })

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Product, TrackedProduct, PriceHistory
from decimal import Decimal, InvalidOperation
from .utils import get_or_create_user_instance  # Import the new function


@csrf_exempt
def track_products_db(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            asin = data.get("asin")
            desired_price = data.get("desired_price")
            current_price = data.get("current_price")

            if not asin:
                return JsonResponse({"error": "ASIN is required."}, status=400)

            # Get the authenticated user
            user_data = get_current_user(request)
            if not user_data:
                return JsonResponse({"error": "User not authenticated."}, status=401)

            user = get_or_create_user_instance(user_data)
            if not user:
                return JsonResponse({"error": "User instance not found."}, status=404)

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
            PriceHistory.objects.create(user=user, product=product, price=current_price)

            return JsonResponse({"success": True})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TrackedProduct
from .utils import  get_or_create_user_instance

@csrf_exempt
def remove_product_db(request, asin):
    """Removes a product from the user's tracked products."""
    if request.method != "DELETE":
        return JsonResponse({"error": "Invalid request method. Only DELETE is allowed."}, status=405)

    # Authenticate User
    user_data = get_current_user(request)
    if not user_data:
        return JsonResponse({"error": "User not authenticated."}, status=401)

    # Fetch user instance
    user = get_or_create_user_instance(user_data)
    if not user:
        return JsonResponse({"error": "User instance not found."}, status=404)

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


