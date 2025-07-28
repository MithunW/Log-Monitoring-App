import argparse
from datetime import datetime

WARNING_THRESHOLD = 300  # 5 minutes in seconds
ERROR_THRESHOLD = 600    # 10 minutes in seconds

def parse_line(line):
    """
    Parse a single log line: TIME, JOB_DESCRIPTION, STATUS, PID
    Example: 11:35:23,scheduled task 032, START,37980
    """
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

def calculate_durations(entries):
    """
    Match START and END for each PID and calculate duration.
    Returns a list of results.
    """
    start_times = {}
    results = []

    for entry in entries:
        pid = entry["pid"]
        if entry["status"] == "START":
            # Record job start
            start_times[pid] = (entry["timestamp"], entry["job"])
        elif entry["status"] == "END":
            if pid in start_times:
                # Calculate duration if START exists
                start_time, job_name = start_times.pop(pid)
                duration = (entry["timestamp"] - start_time).total_seconds()
                results.append({
                    "pid": pid,
                    "job": job_name,
                    "duration": duration,
                    "start": start_time.strftime("%H:%M:%S"),
                    "end": entry["timestamp"].strftime("%H:%M:%S")
                })
            else:
                # END without START
                print(f"Warning: END without START for PID {pid}")
    return results

def evaluate_status(duration):
    if duration > ERROR_THRESHOLD:
        return "ERROR"
    elif duration > WARNING_THRESHOLD:
        return "WARNING"
    return "OK"

def generate_report(results, output_file):
    with open(output_file, "w") as f:
        for res in results:
            status = evaluate_status(res["duration"])
            line = (f"PID: {res['pid']} | Job: {res['job']} | Duration: {int(res['duration'])}s | "
                    f"Start: {res['start']} | End: {res['end']} | Status: {status}")
            print(line)
            f.write(line + "\n")

def run_batch(log_file, output_file):
    entries = []
    try:
        with open(log_file, "r") as f:
            for line in f:
                entry = parse_line(line)
                if entry:
                    entries.append(entry)
    except FileNotFoundError:
        print(f"Error: File '{log_file}' not found.")
        return

    if not entries:
        print("No valid entries found in the log file.")
        return

    results = calculate_durations(entries)
    if not results:
        print("No complete START-END pairs found.")
    else:
        generate_report(results, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log Monitoring Application")
    parser.add_argument("--logfile", default="logs.log", help="Path to the log file")
    parser.add_argument("--output", default="output.log", help="Path to the output file")
    parser.add_argument("--mode", choices=["batch"], default="batch", help="Mode (currently only batch supported)")
    args = parser.parse_args()

    if args.mode == "batch":
        run_batch(args.logfile, args.output)
