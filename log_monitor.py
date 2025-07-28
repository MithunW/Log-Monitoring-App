import argparse
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WARNING_THRESHOLD = 300  # 5 minutes
ERROR_THRESHOLD = 600    # 10 minutes

class LogMonitor:
    def __init__(self, log_file, output_file):
        self.log_file = log_file
        self.output_file = output_file
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
                self.generate_report()  # Update report after every new complete job
            else:
                print(f"Warning: END without START for PID {pid}")

    def evaluate_status(self, duration):
        if duration > ERROR_THRESHOLD:
            return "ERROR"
        elif duration > WARNING_THRESHOLD:
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
            else:
                self.generate_report()
        except FileNotFoundError:
            print(f"Error: File '{self.log_file}' not found.")

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor

    def on_modified(self, event):
        if event.src_path.endswith(self.monitor.log_file):
            with open(self.monitor.log_file, "r") as f:
                for line in f.readlines()[-1:]:  # Read only the last line
                    entry = self.monitor.parse_line(line)
                    if entry:
                        self.monitor.process_entry(entry)

def run_stream(monitor):
    print(f"Starting real-time monitoring on {monitor.log_file}...")
    event_handler = LogFileHandler(monitor)
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log Monitoring Application")
    parser.add_argument("--logfile", default="logs.log", help="Path to the log file")
    parser.add_argument("--output", default="output.log", help="Path to the output file")
    parser.add_argument("--mode", choices=["batch", "stream"], default="batch", help="Mode: batch or stream")
    args = parser.parse_args()

    monitor = LogMonitor(args.logfile, args.output)

    if args.mode == "batch":
        monitor.run_batch()
    else:
        run_stream(monitor)
