import hashlib
import os
import json
import time
import logging
from datetime import datetime
import config

def calculate_file_hash(file_path, block_size=65536):
    """
    Calculates the SHA-256 hash of a single file.
    Reads the file in chunks of 'block_size' bytes so large files
    don't need to be loaded fully into memory.
    """
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()
    except (FileNotFoundError, PermissionError) as e:
        logging.warning(f"Could not read {file_path}: {e}")
        return None

def scan_folder(folder_path):
    """
    Walks through folder_path (including subfolders) and returns a
    dictionary mapping each file's path to its SHA-256 hash.
    """
    file_hashes = {}
    for root, _dirs, files in os.walk(folder_path):
        for filename in files:
            full_path = os.path.join(root, filename)
            file_hash = calculate_file_hash(full_path)
            if file_hash is not None:           # Store using a relative path so the baseline stays  # portable even if the project folder is moved.
                relative_path = os.path.relpath(full_path,folder_path)
                file_hashes[relative_path] = file_hash
    return file_hashes

def create_baseline(folder_path, baseline_path):
    """
    Scans the folder and saves the result as the trusted baseline.
    Run this ONCE, right when you are sure the files are clean.
    """
    file_hashes = scan_folder(folder_path)
    with open(baseline_path, "w") as f:
        json.dump(file_hashes, f, indent=4)
    logging.info(f"Baseline created with {len(file_hashes)} files.")
    print(f"[+] Baseline created successfully with{len(file_hashes)} file(s).")

def load_baseline(baseline_path):
    """
    Loads a previously saved baseline from disk.
    Returns an empty dictionary if no baseline exists yet.
    """
    if not os.path.exists(baseline_path):
        return {}
    with open(baseline_path, "r") as f:
        return json.load(f)

def compare_with_baseline(current_hashes, baseline_hashes):
    """
    Compares the current scan against the baseline.
    Returns a dictionary with three lists: modified, new, deleted.
    """
    modified = []
    new = []
    deleted = []
    for path, current_hash in current_hashes.items():      # Check every file that currently exists
        if path not in baseline_hashes:
            new.append(path)
        elif baseline_hashes[path] != current_hash:
            modified.append(path)
        # else: hash matches -> unchanged, nothing to report
    # Check for files that used to exist but don't anymore
    for path in baseline_hashes:
        if path not in current_hashes:
            deleted.append(path)
    return {"modified": modified, "new": new, "deleted": deleted}

def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def report_changes(changes):
    """
    Prints a clean, human-readable summary to the console and
    writes each detected change to the log file.
    """
    total_changes = len(changes["modified"]) + len(changes["new"]) +len(changes["deleted"])
    if total_changes == 0:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] No changes detected. All files intact.")
        return
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] !! CHANGES DETECTED !!")
    for path in changes["modified"]:
        msg = f"MODIFIED: {path}"
        print(f" [~] {msg}")
        logging.warning(msg)
    for path in changes["new"]:
        msg = f"NEW FILE: {path}"
        print(f" [+] {msg}")
        logging.warning(msg)
    for path in changes["deleted"]:
        msg = f"DELETED: {path}"
        print(f" [-] {msg}")
        logging.warning(msg)

import smtplib
from email.mime.text import MIMEText
def send_email_alert(changes):
    """
    Sends an email summarizing detected changes.
    Only called if config.ENABLE_EMAIL_ALERTS is True.
    """
    body_lines = ["File Integrity Monitor detected the following changes:\n"]
    for kind in ("modified", "new", "deleted"):
        for path in changes[kind]:
            body_lines.append(f"{kind.upper()}: {path}")
            body = "\n".join(body_lines)
            msg = MIMEText(body)
            msg["Subject"] = "FIM Alert: File changes detected"
            msg["From"] = config.SENDER_EMAIL
            msg["To"] = config.RECEIVER_EMAIL
            try:
                with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
                    server.starttls()
                    server.login(config.SENDER_EMAIL,config.SENDER_APP_PASSWORD)
                    server.send_message(msg)
                logging.info("Email alert sent successfully.")
            except Exception as e:
                logging.error(f"Failed to send email alert: {e}")  

def run_single_scan():
    """Performs exactly one scan-and-compare cycle."""
    baseline_hashes = load_baseline(config.BASELINE_FILE)
    if not baseline_hashes:
        print("[!] No baseline found. Creating one now...")
        create_baseline(config.MONITORED_FOLDER,config.BASELINE_FILE)
        return
    current_hashes = scan_folder(config.MONITORED_FOLDER)
    changes = compare_with_baseline(current_hashes, baseline_hashes)
    report_changes(changes)
    total_changes = len(changes["modified"]) + len(changes["new"]) +len(changes["deleted"])
    if total_changes > 0 and config.ENABLE_EMAIL_ALERTS:
        send_email_alert(changes)

def run_continuous_monitor():
    """Repeats the scan every SCAN_INTERVAL_SECONDS, forever, until Ctrl+C."""
    print(f"[*] Monitoring '{config.MONITORED_FOLDER}' every "f"{config.SCAN_INTERVAL_SECONDS} seconds. Press Ctrl+C to stop.\n")
    try:
        while True:
            run_single_scan()
            time.sleep(config.SCAN_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n[*] Monitoring stopped by user.")

def main():
    setup_logging(config.LOG_FILE)  
    print("=" * 50)
    print(" FILE INTEGRITY MONITOR")
    print("=" * 50)
    print("1. Create/Reset Baseline")
    print("2. Run a Single Scan")
    print("3. Start Continuous Monitoring")
    print("4. Exit")
    choice = input("\nSelect an option (1-4): ").strip()
    if choice == "1":
        create_baseline(config.MONITORED_FOLDER,config.BASELINE_FILE)
    elif choice == "2":
        run_single_scan()
    elif choice == "3":
        run_continuous_monitor()
    elif choice == "4":
        print("Goodbye.")
    else:
        print("Invalid choice.")
        
if __name__ == "__main__":
    main()      
