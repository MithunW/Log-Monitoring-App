import argparse
import json
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DEFAULT_WARNING = 300  # 5 minutes
DEFAULT_ERROR = 600    # 10 minutes

class LogMonitor:
    def __init__(self, log_file, output_file, warning_threshold, error_threshold):
        self.log_file = log_file
        self.output_file = output_file
        self.warning_threshold = warning_threshold
        self.error_threshold = error_threshold
        self.start_times = {}
        self.results = []

    def parse_line(self, line):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 4:
            print(f"Skipping malformed line: {line.strip()}")
            return None
        try:
            timestamp = datetime.strptime(parts[0], "%H:%M:%S")
            return {
                "timestamp": timestamp,
                "job": parts[1],
                "status": parts[2].upper(),
                "pid": parts[3]
            }
        except ValueError:
            print(f"Invalid timestamp in line: {line.strip()}")
            return None

    def process_entry(self, entry):
        pid = entry["pid"]
        if entry["status"] == "START":
            self.start_times[pid] = (entry["timestamp"], entry["job"])
        elif entry["status"] == "END":
            if pid in self.start_times:
                start_time, job_name = self.start_times.pop(pid)
                duration = (entry["timestamp"] - start_time).total_seconds()
                self.results.append({
                    "pid": pid,
                    "job": job_name,
                    "duration": duration,
                    "start": start_time.strftime("%H:%M:%S"),
                    "end": entry["timestamp"].strftime("%H:%M:%S")
                })
                self.generate_report()
            else:
                print(f"Warning: END without START for PID {pid}")

    def evaluate_status(self, duration):
        if duration > self.error_threshold:
            return "ERROR"
        elif duration > self.warning_threshold:
            return "WARNING"
        return "OK"

    def generate_report(self):
        with open(self.output_file, "w") as f:
            for res in self.results:
                status = self.evaluate_status(res["duration"])
                line = (f"PID: {res['pid']} | Job: {res['job']} | Duration: {int(res['duration'])}s | "
                        f"Start: {res['start']} | End: {res['end']} | Status: {status}")
                print(line)
                f.write(line + "\n")

    def run_batch(self):
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    entry = self.parse_line(line)
                    if entry:
                        self.process_entry(entry)
            if not self.results:
                print("No complete START-END pairs found.")
        except FileNotFoundError:
            print(f"Error: File '{self.log_file}' not found.")

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor

    def on_modified(self, event):
        if event.src_path.endswith(self.monitor.log_file):
            with open(self.monitor.log_file, "r") as f:
                for line in f.readlines()[-1:]:
                    entry = self.monitor.parse_line(line)
                    if entry:
                        self.monitor.process_entry(entry)

def load_config(config_path):
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            return (
                config.get("warning_threshold_seconds", DEFAULT_WARNING),
                config.get("error_threshold_seconds", DEFAULT_ERROR)
            )
    except FileNotFoundError:
        print(f"No config file found. Using default thresholds.")
    except json.JSONDecodeError:
        print(f"Invalid config format. Using defaults.")
    return DEFAULT_WARNING, DEFAULT_ERROR

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log Monitoring Application")
    parser.add_argument("--logfile", default="logs.log", help="Path to log file")
    parser.add_argument("--output", default="output.log", help="Path to output file")
    parser.add_argument("--mode", choices=["batch", "stream"], default="batch", help="Mode: batch or stream")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    args = parser.parse_args()

    warning_threshold, error_threshold = load_config(args.config)
    monitor = LogMonitor(args.logfile, args.output, warning_threshold, error_threshold)

    if args.mode == "batch":
        monitor.run_batch()
    else:
        print(f"Starting real-time monitoring on {args.logfile}...")
        observer = Observer()
        observer.schedule(LogFileHandler(monitor), ".", recursive=False)    # Monitor current directory. recursive=False(not subdirectories) event handler=LogFileHandler(monitor)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
