import os
import smtplib
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText

# Email environment variables
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")

# Endpoints
VERTICE_URL = "https://booking.vertice.travel/booking"
VERTICE_INFO = "https://www.vertice.travel/alojamiento/paine-grande-shelter-and-camping/"
LASTORRES_URL = "https://book.lastorres.com/Booking/Night?key=01a13887-b4c2-7621-8241-e90b80237d9f&idioma=EN"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}


def send_email_alert(subject: str, message_body: str):
    """Sends an email alert using SMTP_SSL on Port 465."""
    if not SENDER_EMAIL or not SENDER_PASSWORD or not RECIPIENT_EMAIL:
        print("⚠️ Missing email credentials. Skipping email delivery.")
        return

    # Clean password of any accidental spaces
    clean_password = SENDER_PASSWORD.replace(" ", "")

    try:
        msg = MIMEText(message_body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL

        # Port 465 with SSL avoids network/firewall resets
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(SENDER_EMAIL, clean_password)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

        print("✅ Alert email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email alert: {e}")


def check_paine_grande():
    """Checks Paine Grande (Vertice Travel) for Feb 6–7 accommodation."""
    print("Checking Vertice Travel (Paine Grande accommodation - Feb 6-7)...")
    try:
        res = requests.get(VERTICE_URL, headers=HEADERS, timeout=20)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, 'html.parser')
        text = res.text.lower()

        # Check for explicit booking indicators vs sold out indicators
        sold_out_indicators = [
            "agotado", "sold out", "no availability", 
            "sin disponibilidad", "sin cupo", "no hay cupos"
        ]
        
        # Look for active booking buttons or accommodation selection forms
        has_sold_out = any(indicator in text for indicator in sold_out_indicators)
        
        # Verify if an active booking container or form exists
        booking_form = soup.find("form") or soup.find("div", class_=lambda c: c and "booking" in c.lower())

        if booking_form and not has_sold_out:
            msg = (
                "🚨 Accommodation spot detected for Paine Grande (Feb 6-7)!\n\n"
                f"Book now: {VERTICE_URL}\n"
                f"Info page: {VERTICE_INFO}"
            )
            print(msg)
            send_email_alert("🚨 Paine Grande Accommodation Available (Feb 6-7)!", msg)
        else:
            print("Paine Grande Status: Fully Booked.")

    except requests.RequestException as e:
        print(f"❌ Error checking Paine Grande: {e}")


def check_camping_chileno():
    """Checks Camping Chileno (Las Torres) specifically for accommodation for Feb 8–9."""
    print("Checking Las Torres Patagonia (Camping Chileno accommodation - Feb 8-9)...")
    try:
        res = requests.get(LASTORRES_URL, headers=HEADERS, timeout=20)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        text = res.text.lower()

        # Specific terms for Camping / Refugio beds (ignoring meals/extras)
        sold_out_terms = [
            "no availability", "sin disponibilidad", "agotado", 
            "sold out", "no hay disponibilidad", "fully booked"
        ]
        
        is_sold_out = any(term in text for term in sold_out_terms)
        
        # Check for selectable radio buttons or inputs tied to camping/refugio beds
        active_inputs = soup.find_all("input", {"type": ["radio", "checkbox"]})
        has_selectable_options = len(active_inputs) > 0 and not is_sold_out

        if has_selectable_options:
            msg = (
                "🚨 Camping / Accommodation spot detected for Camping Chileno (Feb 8-9)!\n\n"
                f"Book now: {LASTORRES_URL}"
            )
            print(msg)
            send_email_alert("🚨 Camping Chileno Spot Available (Feb 8-9)!", msg)
        else:
            print("Camping Chileno Accommodation Status: Fully Booked.")

    except requests.RequestException as e:
        print(f"❌ Error checking Camping Chileno: {e}")


if __name__ == "__main__":
    check_paine_grande()
    check_camping_chileno()