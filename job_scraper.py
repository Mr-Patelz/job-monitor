import requests
import pandas as pd
import smtplib
import json
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText

# ======================
# CONFIGURATION
# ======================

KEYWORDS = [
    "data engineer",
    "gcp data engineer",
    "gcp developer",
    "cloud data engineer",
    "etl engineer",
    "bigquery",
]

LOCATIONS = [
    "hyderabad",
    "bangalore",
    "bengaluru",
    "india",
    "remote"
]

DAYS_BACK = 7

today = datetime.now()
cutoff = today - timedelta(days=DAYS_BACK)

# ======================
# COMPANY CAREER URLS
# ======================

companies = {

"Microsoft":"https://careers.microsoft.com",
"Google":"https://careers.google.com",
"Amazon":"https://www.amazon.jobs",
"Oracle":"https://careers.oracle.com",
"SAP":"https://jobs.sap.com",
"Salesforce":"https://careers.salesforce.com",
"ServiceNow":"https://careers.servicenow.com",

"TCS":"https://www.tcs.com/careers",
"Infosys":"https://career.infosys.com",
"Wipro":"https://careers.wipro.com",
"HCLTech":"https://www.hcltech.com/careers",
"Tech Mahindra":"https://careers.techmahindra.com",
"LTIMindtree":"https://www.ltimindtree.com/careers",
"Mphasis":"https://www.mphasis.com/careers",
"Persistent":"https://careers.persistent.com",
"Cyient":"https://careers.cyient.com",
"Birlasoft":"https://www.birlasoft.com/careers",

"Accenture":"https://www.accenture.com/careers",
"Cognizant":"https://careers.cognizant.com",
"Capgemini":"https://www.capgemini.com/careers",
"IBM":"https://www.ibm.com/careers",
"Deloitte":"https://jobs.deloitte.com",
"PwC":"https://www.pwc.com/careers",
"EY":"https://careers.ey.com",
"KPMG":"https://home.kpmg/xx/en/home/careers.html",

"Fractal":"https://fractal.ai/careers",
"Tiger Analytics":"https://www.tigeranalytics.com/careers",
"Tredence":"https://www.tredence.com/careers",
"Quantiphi":"https://quantiphi.com/careers",
"MuSigma":"https://www.mu-sigma.com/careers",
"Sigmoid":"https://www.sigmoid.com/careers",

"Darwinbox":"https://darwinbox.com/careers",
"HighRadius":"https://www.highradius.com/careers",
"Freshworks":"https://www.freshworks.com/company/careers",
"OpenText":"https://careers.opentext.com",
"Zoho":"https://www.zoho.com/careers",
"ValueLabs":"https://www.valuelabs.com/careers",

"JPMorgan":"https://careers.jpmorgan.com",
"Goldman Sachs":"https://www.goldmansachs.com/careers",
"Wells Fargo":"https://www.wellsfargojobs.com",
"Citibank":"https://jobs.citi.com",
"HSBC":"https://www.hsbc.com/careers"

}

# ======================
# LOAD PREVIOUS JOBS
# ======================

SEEN_FILE = "seen_jobs.json"

if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE) as f:
        seen_jobs = set(json.load(f))
else:
    seen_jobs = set()

# ======================
# SCRAPE FUNCTION
# ======================

results = []

def keyword_match(text):

    text = text.lower()

    return any(k in text for k in KEYWORDS)

def scrape(company,url):

    try:

        r = requests.get(url,timeout=20)

        text = r.text.lower()

        for keyword in KEYWORDS:

            if keyword in text:

                job_id = company + keyword

                if job_id in seen_jobs:
                    continue

                seen_jobs.add(job_id)

                results.append({

                    "DATE":today.strftime("%Y-%m-%d"),
                    "COMPANY":company,
                    "ROLE":keyword,
                    "LOCATION":"Check JD",
                    "EXP":"Check JD",
                    "LINK":url
                })

    except Exception as e:

        print(company,"error:",e)

# ======================
# RUN SCRAPER
# ======================

for company,url in companies.items():

    scrape(company,url)

# ======================
# SAVE SEEN JOBS
# ======================

with open(SEEN_FILE,"w") as f:

    json.dump(list(seen_jobs),f)

# ======================
# FORMAT EMAIL
# ======================

df = pd.DataFrame(results)

def generate_email_html(df):

    rows = ""

    for _,row in df.iterrows():

        role = row["ROLE"]

        if "gcp" in role.lower():

            role = f"<b style='color:#0b6cff'>⭐ {role}</b>"

        rows += f"""
        <tr>
        <td>{row['DATE']}</td>
        <td>{row['COMPANY']}</td>
        <td>{role}</td>
        <td>{row['LOCATION']}</td>
        <td>{row['EXP']}</td>
        <td>
        <a href="{row['LINK']}"
        style="background:#0b6cff;color:white;padding:6px 12px;text-decoration:none;border-radius:5px;">
        Apply
        </a>
        </td>
        </tr>
        """

    html = f"""
    <html>
    <body>

    <h2>Daily Data Engineer Job Alert</h2>

    <p>
    Total Jobs Found: {len(df)} <br>
    Scan Time: {datetime.now().strftime('%d %b %Y %H:%M')}
    </p>

    <table border="1" cellpadding="6" cellspacing="0">

    <tr style="background:#efefef">
    <th>Date</th>
    <th>Company</th>
    <th>Role</th>
    <th>Location</th>
    <th>Experience</th>
    <th>Apply</th>
    </tr>

    {rows}

    </table>

    <br>

    <small>
    Generated automatically by GitHub Job Monitor
    </small>

    </body>
    </html>
    """

    return html

if df.empty:

    html = "<h3>No new Data Engineer jobs found today</h3>"

else:

    html = generate_email_html(df)

# ======================
# SEND EMAIL
# ======================

sender = os.environ["EMAIL_USER"]
password = os.environ["EMAIL_PASS"]

msg = MIMEText(html,"html")

msg["Subject"]="Daily Data Engineer Job Alert"
msg["From"]=sender
msg["To"]=sender

server = smtplib.SMTP_SSL("smtp.gmail.com",465)

server.login(sender,password)

server.sendmail(sender,sender,msg.as_string())

server.quit()

print("Email sent")
