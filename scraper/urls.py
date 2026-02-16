from django.urls import path
from .views import register_view, login_view, logout_view, google_login, google_callback, home, amazon_product_view, bestsellers_view, result, today_view, tracked_products_view, track_products_db,remove_product_db,schedule_mail,schedule_bestsellers,schedule_today_offers, ping


urlpatterns = [
    path("", home, name="home"),
    path("ping/", ping, name="ping"),
    path('search/', amazon_product_view, name='search'),
    path("register/", register_view, name="register_view"),
    path("login/", login_view, name="login_view"),
    path("logout/", logout_view, name="logout_view"),
    path("google-login/", google_login, name="google_login"),
    path("callback/", google_callback, name="google_callback"),
    path("bestsellers/", bestsellers_view, name="bestsellers_view"),
    path("result/", result, name="result"),
    path("today_view/", today_view, name="today_view"),
    path("tracked-products/", tracked_products_view, name="tracked_products"),
    path("track-products-db/", track_products_db, name="track_products_db"),
    path("remove-product-db/<str:asin>/", remove_product_db, name="remove_product_db"),
    path('sendmail/',schedule_mail,name='send-mail'),
    path('sendbestseller/',schedule_bestsellers,name='sendbestseller'),
    path('sendtoady_offer/',schedule_today_offers,name='sendbestseller'),
]




