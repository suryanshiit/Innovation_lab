import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Sender and Receiver details
sender_email = "suryanshkgp@gmail.com"
receiver_email = "suryansh16103@gmail.com"
password = "mergexcgbqlnfhbk"  # Use an app password if using Gmail

# Create Email Message
subject = "Test Email using SMTP"
body = "Hello, this is a test email sent using Python."

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain"))

# Connect to SMTP Server and Send Email
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()  # Secure connection
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    print("Email sent successfully!")
except Exception as e:
    print("Error:", e)
finally:
    server.quit()
