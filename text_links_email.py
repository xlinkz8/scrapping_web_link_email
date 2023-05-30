
import os
import re
import requests
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Rest of the code remains the same


def extract_pattern(text, pattern):
    return re.findall(pattern, text)

def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    excel_path = f"{filename}.xlsx"  # Provide a fixed file path and filename
    df.to_excel(excel_path, index=False, engine='openpyxl')  # Specify the engine as 'openpyxl'
    return excel_path


def send_email(sender_email, sender_password, receiver_email, subject, body, attachment_path=None):
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    if attachment_path:
        attachment = open(attachment_path, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % os.path.basename(attachment_path))
        message.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()


def main():
    url = input("Enter the website URL: ")
    sender_email = input("Enter the sender email address: ")
    sender_password = input("Enter the sender email password: ")
    receiver_email = input("Enter the receiver email address: ")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for any HTTP errors
        html_content = response.text

        phone_numbers = extract_pattern(html_content, r"234[789][01]\d{8}\b")
        emails = extract_pattern(html_content, r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        links = extract_pattern(html_content, r'<a\s+(?:[^>]?\s+)?href="([^"]*)"')

        phone_numbers_file = save_to_excel(phone_numbers, 'phone_numbers')
        emails_file = save_to_excel(emails, 'emails')
        links_file = save_to_excel(links, 'links')

        print("Extraction complete. Phone numbers, emails, and links saved as Excel files.")

        subject = "Web Scraping Results"
        body = "Please find the attached files containing the extracted data."

        send_email(sender_email, sender_password, receiver_email, subject, body, phone_numbers_file)
        send_email(sender_email, sender_password, receiver_email, subject, body, emails_file)
        send_email(sender_email, sender_password, receiver_email, subject, body, links_file)

        print("Emails sent with the saved files.")
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while retrieving the webpage: {e}")
main()