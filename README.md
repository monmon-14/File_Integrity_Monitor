#  File Integrity Monitor (FIM)

A Python-based **File Integrity Monitor** that detects unauthorized changes — modifications, new files, and deletions — inside a monitored directory using **SHA-256 cryptographic hashing**.

This project demonstrates the same core technique used by real-world Host-based Intrusion Detection Systems (HIDS) such as **Tripwire**, **OSSEC**, and the **Wazuh FIM module**: take a trusted snapshot of file hashes (a *baseline*), then continuously compare the current state of the file system against it to catch tampering.

---

## ✨ Features

- **Baseline creation** — scans a target folder (including subfolders) and records a SHA-256 hash for every file.
- **Change detection** — classifies every scan result as `MODIFIED`, `NEW`, or `DELETED`.
- **Persistent logging** — every scan and every detected change is timestamped and written to `fim_log.txt` for audit purposes.
- **Continuous monitoring mode** — automatically re-scans on a configurable interval.
- **Windows Task Scheduler integration** — supports production-style scheduled runs instead of a manually running terminal window.
- **Optional email alerts** — sends a summary email via SMTP when changes are detected.
- **Optional GUI** — a simple Tkinter interface as an alternative to the command-line menu.

---

## 🧠 How It Works

1. **Baseline** — On first run, the tool walks through the monitored folder and computes a SHA-256 hash for every file, storing the results in `baseline.json`.
2. **Scan** — On each subsequent run, it recomputes the hashes and compares them against the baseline.
3. **Compare** —
   - Path exists now but wasn't in the baseline → **New file**
   - Path exists in both but the hash differs → **Modified file**
   - Path was in the baseline but is missing now → **Deleted file**
4. **Report** — Results are printed to the console and logged with timestamps. Optionally, an email alert is sent.

Because SHA-256 has the *avalanche effect*, even a single-byte change to a file produces a completely different hash — making tampering easy to detect without storing full file copies.

---

## 🛠️ Tech Stack

- **Python 3.12+**
- Built-in libraries: `hashlib`, `os`, `json`, `time`, `logging`, `smtplib`, `colorama`

---

## 📂 Project Structure

```
FileIntegrityMonitor/
│
├── monitored_folder/     # Folder being watched for changes (sample/demo data)
├── fim.py                # Main program (CLI)
├── config.py              # Central configuration (paths, scan interval, email settings)
├── baseline.json          # Auto-generated trusted hash snapshot (gitignored)
├── fim_log.txt            # Auto-generated activity log (gitignored)
```

---

## 🚀 Getting Started (Windows)

### 1. Clone the repository

```bat
git clone https://github.com/monmon-14/File_Integrity_Monitor.git
cd File_Integrity_Monitor
```

### 2. Create and activate a virtual environment

```bat
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bat
python -m pip install colorama
```

### 4. Configure the monitored folder

Edit `config.py` and set `MONITORED_FOLDER` to the directory you want to watch.

### 5. Run the program

```bat
python fim.py
```

Choose from the menu:
```
1. Create/Reset Baseline
2. Run a Single Scan
3. Start Continuous Monitoring
4. Exit
```

---

## ⏱️ Automating with Windows Task Scheduler

For "always-on" protection without keeping a terminal window open, register `run_fim.bat` as a recurring Windows Task Scheduler task (e.g. every 10 minutes). See the project write-up for full step-by-step instructions.

---

## ⚠️ Known Limitations

- **Baseline trust problem**: the baseline is only as trustworthy as the moment it was created — if files are already tampered with before the baseline runs, the tool will treat the compromised state as "normal."
- **Rename blind spot**: a renamed file is reported as one deletion + one new file, since the tool tracks `(path, hash)` pairs rather than persistent file identity.
- **Baseline file itself is not tamper-proof**: an attacker with write access to `baseline.json` could update it to match a malicious file. A production version should sign the baseline (e.g. with HMAC) or store it off-host.
- **Polling, not real-time**: changes are only caught on the next scan interval, not the instant they happen (a future version could use the `watchdog` package for real-time OS-level file events).

---

## 🔮 Possible Extensions

- Real-time monitoring via the `watchdog` package
- HMAC-signed baseline to prevent silent baseline tampering
- SQLite-backed baseline for large-scale monitoring
- Multi-folder monitoring with independent baselines
- Web dashboard (Flask) for browser-based scan history

---

## 📄 License

This project is for educational purposes.

---

## 👤 Author

Built by Monisha M — CSE Undergraduate.
