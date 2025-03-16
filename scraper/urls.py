from django.urls import path
from .views import register_view, login_view, logout_view, google_login, google_callback, home, amazon_product_view, bestsellers_view, load_more_products, result, today_view, load_deal_products, tracked_products_view, track_products_db,remove_product_db
# bestseller_list

urlpatterns = [
    path("", home, name="home"),
    path('search/', amazon_product_view, name='search'),
    path("register/", register_view, name="register_view"),
    path("login/", login_view, name="login_view"),
    path("logout/", logout_view, name="logout_view"),
    path("google-login/", google_login, name="google_login"),
    path("callback/", google_callback, name="google_callback"),
    path("bestsellers/", bestsellers_view, name="bestsellers_view"),
    path("load-more-products/", load_more_products, name="load_more_products"),
    path("result/", result, name="result"),
    path("today_view/", today_view, name="today_view"),
    path("load-deal-products/", load_deal_products, name="load_deal_products"), 
    
    # path("price_watch/", price_watch, name="price_watch"),

    path("tracked-products/", tracked_products_view, name="tracked_products"),
    
    path("track-products-db/", track_products_db, name="track_products_db"),
    path("remove-product-db/<str:asin>/", remove_product_db, name="remove_product_db"),
    # path("bestsellers/", bestseller_list, name="bestseller_list"),
    # path("todaydeals_list/", todaydeals_list, name="todaydeals_list"),
]




