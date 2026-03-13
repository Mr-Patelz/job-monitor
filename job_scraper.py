import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import os

KEYWORDS = [
    "gcp data engineer",
    "data engineer",
    "gcp developer"
]

LOCATIONS = [
    "india",
    "hyderabad",
    "bangalore",
    "bengaluru",
    "pune",
    "chennai"
]

companies = {
    "Infosys": "https://career.infosys.com",
    "Wipro": "https://careers.wipro.com",
    "Cognizant": "https://careers.cognizant.com",
    "Capgemini": "https://www.capgemini.com/careers",
    "HCL": "https://www.hcltech.com/careers",
    "IBM": "https://www.ibm.com/careers",
    "Accenture": "https://www.accenture.com/careers",
    "Tech Mahindra": "https://careers.techmahindra.com",
    "CGI": "https://cgi.njoyn.com"
}

results = []
visited_links = set()

today = datetime.now()
yesterday = today - timedelta(days=1)

def match_keywords(title):
    title = title.lower()
    return any(k in title for k in KEYWORDS)

def scrape_company(company, url):
    try:
        response = requests.get(url, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.find_all("a")

        for link in links:

            title = link.text.strip()
            href = link.get("href")

            if not title or not href:
                continue

            if href in visited_links:
                continue

            if match_keywords(title):

                visited_links.add(href)

                results.append({
                    "POSTED DATE": today.strftime("%Y-%m-%d"),
                    "COMPANY": company,
                    "ROLE": title,
                    "LOCATION": "Check JD",
                    "EXPERIENCE": "Check JD",
                    "LINK": href
                })

    except Exception as e:
        print(company, "error:", e)


for company, url in companies.items():
    scrape_company(company, url)

df = pd.DataFrame(results)

if not df.empty:
    df = df.drop_duplicates(subset=["LINK"])

html_table = df.to_html(index=False, escape=False)

sender = os.environ["EMAIL_USER"]
password = os.environ["EMAIL_PASS"]
receiver = os.environ["EMAIL_USER"]

msg = MIMEText(html_table, "html")

msg["Subject"] = "Daily GCP/Data Engineer Jobs"
msg["From"] = sender
msg["To"] = receiver

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

server.login(sender, password)

server.sendmail(sender, receiver, msg.as_string())

server.quit()

print("Job report email sent")