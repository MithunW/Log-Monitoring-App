import unittest
from datetime import datetime
from log_monitor import LogMonitor

class TestLogMonitor(unittest.TestCase):

    def setUp(self):
        self.monitor = LogMonitor("dummy.log", "dummy_output.log", 300, 600)  # Add thresholds

    # -------------------
    # BASIC FUNCTIONALITY TESTS
    # -------------------
    def test_parse_valid_line(self):
        line = "11:35:23,scheduled task 032, START,37980"
        result = self.monitor.parse_line(line)
        self.assertIsNotNone(result)
        self.assertEqual(result["pid"], "37980")
        self.assertEqual(result["job"], "scheduled task 032")
        self.assertEqual(result["status"], "START")

    def test_parse_invalid_line_format(self):
        result = self.monitor.parse_line("invalid line format")
        self.assertIsNone(result)

    def test_calculate_duration(self):
        start_time = datetime.strptime("11:35:23", "%H:%M:%S")
        end_time = datetime.strptime("11:40:23", "%H:%M:%S")
        self.monitor.start_times["123"] = (start_time, "Test Job")
        entry = {"timestamp": end_time, "pid": "123", "status": "END", "job": "Test Job"}
        self.monitor.process_entry(entry)
        self.assertEqual(len(self.monitor.results), 1)
        self.assertEqual(self.monitor.results[0]["duration"], 300)

    def test_status_ok_warning_error(self):
        self.assertEqual(self.monitor.evaluate_status(100), "OK")
        self.assertEqual(self.monitor.evaluate_status(400), "WARNING")
        self.assertEqual(self.monitor.evaluate_status(700), "ERROR")

    # -------------------
    # EDGE CASE TESTS
    # -------------------
    def test_invalid_timestamp(self):
        result = self.monitor.parse_line("invalid_time, scheduled task, START, 123")
        self.assertIsNone(result)

    def test_end_without_start(self):
        entry = {"timestamp": datetime.strptime("12:10:00", "%H:%M:%S"), "pid": "1", "status": "END", "job": "Job1"}
        self.monitor.process_entry(entry)
        self.assertEqual(len(self.monitor.results), 0)  # No pair created

    def test_start_without_end(self):
        entry = {"timestamp": datetime.strptime("12:00:00", "%H:%M:%S"), "pid": "1", "status": "START", "job": "Job1"}
        self.monitor.process_entry(entry)
        self.assertEqual(len(self.monitor.results), 0)  # Still waiting for END

    def test_duplicate_start_before_end(self):
        entry1 = {"timestamp": datetime.strptime("12:00:00", "%H:%M:%S"), "pid": "1", "status": "START", "job": "Job1"}
        entry2 = {"timestamp": datetime.strptime("12:01:00", "%H:%M:%S"), "pid": "1", "status": "START", "job": "Job1"}
        self.monitor.process_entry(entry1)
        self.monitor.process_entry(entry2)
        self.assertEqual(len(self.monitor.results), 0)

    def test_mixed_order_logs(self):
        end_entry = {"timestamp": datetime.strptime("12:05:00", "%H:%M:%S"), "pid": "1", "status": "END", "job": "Job1"}
        start_entry = {"timestamp": datetime.strptime("12:00:00", "%H:%M:%S"), "pid": "1", "status": "START", "job": "Job1"}
        self.monitor.process_entry(end_entry)
        self.monitor.process_entry(start_entry)
        self.assertEqual(len(self.monitor.results), 0)  # Wrong order, so ignored

if __name__ == "__main__":
    unittest.main()
