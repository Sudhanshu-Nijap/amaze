# Amaze

**Amaze** — Amazon Price Tracker

## 📄 Description  

Amaze is a web application that lets users track Amazon product prices and stock availability over time.  
Users can submit a product URL or ASIN, view product details, price history, reviews, and stock status.  
Price-watch thresholds can be set, and email notifications are sent when prices drop or products are back in stock.  

The app also displays Amazon best-sellers and today’s deals, with infinite scroll.  
Data is stored in Supabase, and scraping tasks are scheduled using Celery.  

## ✅ Features  

- Track Amazon products by URL or ASIN  
- View product details: title, price, stock status, images  
- See price history charts for tracked products  
- Set price-watch thresholds for notifications  
- Receive email notifications for price drops or stock updates  
- Browse Amazon best-sellers and today’s deals  
- Scheduled scraping using Celery tasks  
- User authentication with Supabase  

## 🧰 Tech Stack  

- **Backend:** Django (Python)  
- **Task Scheduler:** Celery  
- **Database:** Supabase  
- **Frontend:** HTML, CSS, JS
- **Web Scraping:** Python (BeautifulSoup / requests / Selenium)  
- **Email Notifications:** Django `send_mail`
- **API's:** Scraper API 

## 📦 Installation & Setup  

> **Prerequisites:** Python 3.x, pip, virtualenv, Supabase account  

```bash
# Clone the repo
git clone https://github.com/Sudhanshu-Nijap/amaze.git
cd amaze

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
# Copy `.env.example` → `.env` and fill in Supabase and email credentials

# Apply migrations
python manage.py migrate

# (Optional) Create superuser
python manage.py createsuperuser

# Run Celery worker for periodic scraping
celery -A amaze worker --beat --scheduler django -l info

# Start the Django development server
python manage.py runserver

# Open http://localhost:8000 in your browser
