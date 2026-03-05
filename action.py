import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import geocoder
from datetime import datetime
from dotenv import load_dotenv

import asyncio
from winsdk.windows.devices.geolocation import Geolocator
load_dotenv()
sender_email = os.getenv("SENDER_EMAIL")
app_password = os.getenv("APP_PASSWORD")

async def _get_coords():
    locator = Geolocator()
    pos = await locator.get_geoposition_async()

    lat = pos.coordinate.latitude
    lon = pos.coordinate.longitude

    return lat, lon


def get_location():
    try:
        lat, lon = asyncio.run(_get_coords())
    except Exception as e:
        print("Location error:", e)
        lat, lon = 0, 0

    maps_link = f"https://maps.google.com/?q={lat},{lon}"

    return {
        "lat": lat,
        "lon": lon,
        "link": maps_link
    }
emails = os.getenv("emergency_emails")
emergency_emails = emails.split(",") if emails else []
def get_recent_conversation(lines=10):
  
    path = "memory/conversation_log.txt"

    if not os.path.exists(path):
        return "No conversation history."

    with open(path, "r", encoding="utf-8") as f:
        content = f.readlines()

    last_lines = content[-lines:]

    return "".join(last_lines)

def log_event(report):
    print("\n[LOG] Normal monitoring")
    print(report)

def start_recording():
    print("[ACTION] Recording intensified...")


def trigger_alarm():
    print("[ACTION] Alarm triggered")


def flash_light():
    print("[ACTION] Flashlight ON")



def share_live_location():

    location = get_location()

    print("\n📍 Sharing Live Location")
    print(location["link"])

    return location

def get_recent_audio():

    file_path = "recordings/latest.wav"

    if os.path.exists(file_path):
        print("Audio evidence found")
        return file_path

    print("No audio evidence")
    return None

def build_alert_message(report, location):

    conversation = get_recent_conversation()

    message = f"""
🚨 EMERGENCY ALERT
User may be in danger.

Time: {report['time']}
Risk Level: {report['risklevel']}
📍 Live Location:
{location['link']}
🗣 Recent Conversation:
{conversation}

"""

    return message


def send_emergency_alert(report):

    location = share_live_location()

    subject = "🚨 EMERGENCY ALERT"

    body = build_alert_message(report, location)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)

        for email in emergency_emails:

            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            server.sendmail(app_password, email, msg.as_string())

            print(f"📨 Email sent to {email}")

        server.quit()

    except Exception as e:
        print("Email failed:", e)

    return location

def deterrence_voice():
    print("\n📢 Speaking deterrence message")
    print("Your actions are being recorded. Authorities have been notified.")


def start_location_tracking():
    print("📍 Continuous location tracking started")


def action_layer(decision, report):
    print("im reaching here")
    action = decision.get("action")

    if action == "LOG":

        print("\nNormal monitoring")

    elif action == "MONITOR":

        print("\n⚠ Suspicious situation")

        start_recording()
        start_location_tracking()

    elif action == "ALERT":

        print("\n🚨 DANGER DETECTED")

        location = send_emergency_alert(report)

        audio = get_recent_audio()

        if audio:
            print(f"📎 Sending audio clip: {audio}")

        start_location_tracking()

        deterrence_voice()
        trigger_alarm()
        flash_light()

    else:
        print("Unknown action")