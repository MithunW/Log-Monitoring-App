import unittest
import os
from log_monitor import LogMonitor

class TestEndToEnd(unittest.TestCase):

    def setUp(self):
        # Create a sample log file with different scenarios
        self.log_file = "sample_test.log"
        self.output_file = "sample_output.log"
        with open(self.log_file, "w") as f:
            f.write("11:00:00,job1, START,1001\n")     # Job1 start
            f.write("11:04:00,job1, END,1001\n")       # Duration: 4 mins (OK)
            f.write("11:05:00,job2, START,1002\n")     # Job2 start
            f.write("11:15:30,job2, END,1002\n")       # Duration: 10.5 mins (ERROR)
            f.write("11:20:00,job3, START,1003\n")     # Job3 start
            f.write("11:26:00,job3, END,1003\n")       # Duration: 6 mins (WARNING)
            f.write("invalid_line\n")                  # Malformed line
            f.write("11:30:00,job4, END,9999\n")       # END without START
            f.write("invalid_time,job5, START,1005\n") # Invalid timestamp

    def tearDown(self):
        # Remove temporary files after test
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_end_to_end_processing(self):
        monitor = LogMonitor(self.log_file, self.output_file)
        monitor.run_batch()

        # Verify output file exists
        self.assertTrue(os.path.exists(self.output_file))

        # Check contents for OK, WARNING, ERROR
        with open(self.output_file, "r") as f:
            content = f.read()
            self.assertIn("OK", content)
            self.assertIn("WARNING", content)
            self.assertIn("ERROR", content)

        # Check correct number of completed jobs processed (3 valid jobs)
        lines = content.strip().split("\n")
        self.assertEqual(len(lines), 3)

if __name__ == "__main__":
    unittest.main()
