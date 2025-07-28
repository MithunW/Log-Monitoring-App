import unittest
from datetime import datetime
from log_monitor import LogMonitor

class TestLogMonitorBasic(unittest.TestCase):

    def setUp(self):
        # Use a dummy output file for tests
        self.monitor = LogMonitor("dummy.log", "dummy_output.log")

    def test_parse_valid_line(self):
        line = "11:35:23,scheduled task 032, START,37980"
        result = self.monitor.parse_line(line)
        self.assertIsNotNone(result)
        self.assertEqual(result["pid"], "37980")
        self.assertEqual(result["job"], "scheduled task 032")
        self.assertEqual(result["status"], "START")

    def test_parse_invalid_line_format(self):
        line = "invalid line format"
        result = self.monitor.parse_line(line)
        self.assertIsNone(result)

    def test_calculate_duration(self):
        start_time = datetime.strptime("11:35:23", "%H:%M:%S")
        end_time = datetime.strptime("11:40:23", "%H:%M:%S")
        self.monitor.start_times["123"] = (start_time, "Test Job")
        entry = {"timestamp": end_time, "pid": "123", "status": "END", "job": "Test Job"}
        self.monitor.process_entry(entry)
        self.assertEqual(len(self.monitor.results), 1)
        self.assertEqual(self.monitor.results[0]["duration"], 300)  # 5 minutes

    def test_status_ok_warning_error(self):
        self.assertEqual(self.monitor.evaluate_status(100), "OK")
        self.assertEqual(self.monitor.evaluate_status(400), "WARNING")
        self.assertEqual(self.monitor.evaluate_status(700), "ERROR")

if __name__ == "__main__":
    unittest.main()
