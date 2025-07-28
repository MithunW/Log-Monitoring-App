# Log Monitoring Application

This application processes system logs to track job execution times and generate alerts if processing times exceed defined thresholds.

---

## ✅ Features
- **Batch Mode**: Reads the entire log file once and produces a report.
- **Stream Mode (Real-Time)**: Monitors the log file continuously for new entries and updates the report dynamically.
- Alerts:
  - **OK** → Job completed within 5 minutes.
  - **WARNING** → Job took longer than 5 minutes.
  - **ERROR** → Job took longer than 10 minutes.
- Handles malformed lines, invalid timestamps, and missing START/END gracefully.
- Includes:
  - **Unit Tests** (logic validation)
  - **End-to-End Tests** (full file processing)
- Dockerized for portability and includes CI/CD workflow for automated testing.

---

## ✅ Modes Explained

### **Batch Mode**
- Best for **static log analysis**.
- Reads the entire log file in one go and generates a summary report.
- Example:
```bash
python log_monitor.py --logfile logs.log --output output.log --mode batch
```

### **Stream Mode (Real-Time)**
- Best for **live monitoring**.
- Continuously watches the log file for changes using `watchdog`.
- Processes new log entries as they arrive and updates the report dynamically.
- Example:
```bash
python log_monitor.py --logfile logs.log --output output.log --mode stream
```

---

## ✅ How It Works
- Each log line should follow this format:
```
TIME, JOB_DESCRIPTION, STATUS, PID
Example: 11:35:23,scheduled task 032, START,37980
```
- The application pairs `START` and `END` entries for the same PID to compute duration.
- Generates a report showing:
```
PID: 37980 | Job: scheduled task 032 | Duration: 33s | Start: 11:35:23 | End: 11:35:56 | Status: OK
```

---

## ✅ Run Tests
To run all tests:
```bash
python -m unittest discover tests
```

---

## ✅ Run with Docker
Build image:
```bash
docker build -t log-monitor .
```
Run container:
```bash
docker run -v $(pwd):/app log-monitor
```

---

## ✅ CI/CD
- The included GitHub Actions workflow (`.github/workflows/ci.yml`) automatically:
  - Installs dependencies
  - Runs unit and integration tests
- Triggered on every push and pull request to the `main` branch.

---
