# Log Monitoring Application

A coding challenge solution for DevOps Engineer role.

---

## ✅ Features
- Parses CSV log files and computes job durations.
- Generates alerts:
  - **OK**: Duration ≤ 5 minutes
  - **WARNING**: Duration > 5 minutes
  - **ERROR**: Duration > 10 minutes
- Handles **malformed lines** and **missing START/END gracefully**.
- Supports **configurable thresholds** via `config.json`.
- Provides **real-time monitoring** with file watchers.
- Includes **unit tests and end-to-end tests**.
- CLI interface for easy usage.

---

## ✅ Config File
`config.json`:
```json
{
    "warning_threshold_seconds": 300,
    "error_threshold_seconds": 600
}
```

---

## ✅ How to Run

### **Batch Mode**
```bash
python3 log_monitor.py --logfile logs.log --config config.json --mode batch
```

### **Streaming Mode**
```bash
python3 log_monitor.py --logfile logs.log --config config.json --mode stream
```

---

## ✅ Tests
Run all tests:
```bash
python3 -m unittest discover tests
```

---

## ✅ Possible Improvements
- Integrate monitoring tool like Datadog or similar to push the monitoring matrices to a dashboard.
- Integrate serviceNow or similar tool to escalate alerts to developers.
- Add REST API endpoints.
- Dockerize application.
- Support log rotation.

---


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

## ✅ GitHub Actions CI/CD
- The repo includes a workflow file `.github/workflows/ci.yml`.
- On every `push` or `pull request` to `main`, the pipeline:
  - Checks out code
  - Sets up Python
  - Installs dependencies
  - Runs unit and end-to-end tests

---


---

## ✅ Dependencies
All Python dependencies are listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

---
