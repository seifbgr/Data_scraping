#  AliExpress Web Scraper (Microphons) (Selenium + Python)

This project is a fully automated **AliExpress product scraper** built with `Selenium`, designed to collect data from search result pages such as product titles, prices, ratings, discounts, and URLs.

---

## Target :
This scraper targets the following page:https://www.aliexpress.us/w/wholesale-microphone.html?g=y&SearchText=microphone

---

##  Features

-  Scrapes up to 60 pages of product listings  
-  Extracts key fields: title, price, discount, ratings, number of orders, link  
-  Handles dynamic content loading via smart scrolling  
-  Manages cookie banners and pop-ups  
-  Bypasses basic anti-bot detection (custom User-Agent, WebDriver masking)  
-  Automatically saves data to CSV every 5 pages to prevent loss  
-  Three-layered fallback system for page navigation (Next button, page numbers, direct URL)

---

##  Technologies Used

- Python 3.x  
- Selenium WebDriver  
- ChromeDriver  
- Pandas  
- XPath for element selection  

---

##  Extracted Fields

- `titles` – Product name  
- `prices` – Current price  
- `prices_bef` – Price before discount (if available)  
- `Ranting` – Rating  
- `sold` – Number of units sold  
- `Discount` – Discount percentage (if shown)  
- `liens` – Direct product URL  

---

##  How It Works

1. Opens the AliExpress search page (e.g. "microphone")
2. Accepts cookies and closes pop-ups if detected
3. Scrolls down with randomized pauses (mimicking human behavior)
4. Extracts product data per page
5. Navigates through pagination (Next, number or direct URL)
6. Saves data incrementally into CSV files
7. At the end, merges everything into `Ali_chaise_complet.csv`

---

##  Output Example

Output is a CSV file structured like this:

| Title                 | Price | Old Price | Rating | Sold | Discount | URL                        |
|----------------------|-------|-----------|--------|------|----------|-----------------------------|
| USB Microphone XYZ   | $29   | $39       | 4.8    | 2345 | -25%     | https://...                |

---

##  Disclaimer

This scraper is for educational and research purposes. Use responsibly and respect AliExpress’s [terms of service](https://www.aliexpress.com/policies/terms.html).

---

##  To Run the Script

1. Install dependencies:
   ```bash
   pip install selenium pandas
