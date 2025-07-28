from datetime import datetime

LOG_FILE = "logs.log"
OUTPUT_FILE = "output.log"

WARNING_THRESHOLD = 300  # 5 minutes in seconds
ERROR_THRESHOLD = 600    # 10 minutes in seconds

def parse_line(line):
    """
    Parse a single log line: TIME, JOB_DESCRIPTION, STATUS, PID
    Example: 11:35:23,scheduled task 032, START,37980
    """
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 4:
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
            start_times[pid] = (entry["timestamp"], entry["job"])
        elif entry["status"] == "END" and pid in start_times:
            start_time, job_name = start_times.pop(pid)
            duration = (entry["timestamp"] - start_time).total_seconds()
            results.append({
                "pid": pid,
                "job": job_name,
                "duration": duration,
                "start": start_time.strftime("%H:%M:%S"),
                "end": entry["timestamp"].strftime("%H:%M:%S")
            })
    return results

def generate_report(results):
    """
    Print and write report to OUTPUT_FILE.
    """
    with open(OUTPUT_FILE, "w") as f:
        for res in results:
            status = "OK"
            if res["duration"] > ERROR_THRESHOLD:
                status = "ERROR"
            elif res["duration"] > WARNING_THRESHOLD:
                status = "WARNING"
            line = (f"PID: {res['pid']} | Job: {res['job']} | Duration: {int(res['duration'])}s | "
                    f"Start: {res['start']} | End: {res['end']} | Status: {status}")
            print(line)
            f.write(line + "\n")

def main():
    entries = []
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                entry = parse_line(line)
                if entry:
                    entries.append(entry)
    except FileNotFoundError:
        print(f"Error: File '{LOG_FILE}' not found.")
        return

    results = calculate_durations(entries)
    generate_report(results)

if __name__ == "__main__":
    main()
