import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import os
import re

KEYWORDS = [
    "gcp data engineer",
    "data engineer",
    "gcp developer"
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
seven_days_ago = today - timedelta(days=7)


def keyword_match(title):
    title = title.lower()
    return any(k in title for k in KEYWORDS)


def parse_posted_days(text):
    """
    Extract 'X days ago' from job text
    """
    match = re.search(r'(\d+)\s+day', text.lower())
    if match:
        days = int(match.group(1))
        return today - timedelta(days=days)

    if "today" in text.lower():
        return today

    return None


def scrape_company(company, url):

    try:

        response = requests.get(url, timeout=20)

        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a"):

            title = link.text.strip()

            href = link.get("href")

            if not title or not href:
                continue

            if href in visited_links:
                continue

            if keyword_match(title):

                posted_date = parse_posted_days(title)

                if posted_date and posted_date < seven_days_ago:
                    continue

                visited_links.add(href)

                results.append({
                    "POSTED DATE": posted_date.strftime("%Y-%m-%d") if posted_date else "Recent",
                    "COMPANY": company,
                    "ROLE": title,
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

msg["Subject"] = "Last 7 Days – MNC GCP/Data Engineer Jobs"
msg["From"] = sender
msg["To"] = receiver


server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

server.login(sender, password)

server.sendmail(sender, receiver, msg.as_string())

server.quit()

print("Email sent successfully")
