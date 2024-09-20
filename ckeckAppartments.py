import time
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Function to send an email notification
def send_email(new_apartment_info):
    sender_email = "your_email@gmail.com"
    receiver_email = "serhiy.ivanko@gmail.com"
    password = "your_email_password"

    # Set up the message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "New Apartment Available"

    body = f"New apartment found:\n\n{new_apartment_info}"
    message.attach(MIMEText(body, "plain"))

    try:
        # Send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


# Function to check for new apartments
def check_new_apartments():
    url = "https://vantagerent.pl/%d1%88%d1%83%d0%ba%d0%b0%d1%82%d0%b8-%d0%ba%d0%b2%d0%b0%d1%80%d1%82%d0%b8%d1%80%d1%83/?lang=pl&pg=1&posts_per_page=10&layout=list&city_id=8&display_starred=1&number_of_rooms%5B0%5D=4&sort_value=local_available_from&sort_direction=ASC"
    response = requests.get(url)
    print(response.content)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract information about apartments
    apartments = soup.find_all("div", class_="offer-list__item")  # Adjust this based on the actual structure

    print(apartments)

    # Here we define the known apartment (you may need to update this if the original information changes)
    known_apartment = "---" # "Skowrońskiego 2/1 Comfort style 4 Parter 75.76m2 Już dzisiaj 3703 PLN/MC"

    # List to store information of current apartments
    current_apartments = []

    # Parse the apartments and check for new listings
    for apartment in apartments:
        apartment_info = apartment.get_text(separator=" ").strip()
        current_apartments.append(apartment_info)

    # Check for any new apartment
    new_apartments = [apt for apt in current_apartments if apt != known_apartment]

    if new_apartments:
        for new_apartment in new_apartments:
            print(f"New apartment found: {new_apartment}")
            send_email(new_apartment)
    else:
        print("No new apartments found.")


# Main function to run the script periodically
if __name__ == "__main__":
    while True:
        check_new_apartments()
        time.sleep(3600)  # Check every hour
