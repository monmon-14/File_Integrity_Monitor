# config.py
# Central configuration for the File Integrity Monitor.


MONITORED_FOLDER = r"monitored_folder"     # Where the trusted baseline of hashes is stored.
BASELINE_FILE = "baseline.json"            # Where all scan activity is logged.
LOG_FILE = "fim_log.txt"
SCAN_INTERVAL_SECONDS = 10                 # How often (in seconds) the continuous monitor re-scans the folder.

# --- email alert settings ---
# Leave ENABLE_EMAIL_ALERTS = False until you have configured a real sender account. Gmail requires an "App Password", not your normal password.
ENABLE_EMAIL_ALERTS = False
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_APP_PASSWORD = "your_16_char_app_password"
RECEIVER_EMAIL = "your_email@gmail.com"