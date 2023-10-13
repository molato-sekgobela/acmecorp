import unittest

# Define a test case class for verifying the file structure of `example_data.txt`.
class TestFileStructure(unittest.TestCase):

    def test_txt_structure(self):
        """Test if the structure (headers) of the example_data.txt file is as expected."""
        with open('example_data.txt', 'r') as f:
            # Read the first line of the file to check the header/column names.
            header = f.readline().strip().split(',')
            
            # Assert if the header matches the expected structure.
            self.assertListEqual(header, ["device_id", "timestamp", "temperature", "humidity", "hvac_status"])

if __name__ == "__main__":
    unittest.main()
