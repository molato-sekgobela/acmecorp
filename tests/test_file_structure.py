import unittest

class TestFileStructure(unittest.TestCase):

    def test_txt_structure(self):
        with open('example_data.txt', 'r') as f:
            # Read the first line to check the header/column names
            header = f.readline().strip().split(',')
            self.assertListEqual(header, ["device_id", "timestamp", "temperature", "humidity", "hvac_status"])

if __name__ == "__main__":
    unittest.main()
