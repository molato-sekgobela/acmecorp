import unittest
from unittest.mock import patch, Mock, MagicMock
from read_from_rds import lambda_function as retrieve_func
import json


class TestLambdaFunctionRetrieve(unittest.TestCase):
    """
    Test cases for the lambda function that retrieves data from an RDS instance.
    """

    @patch("mysql.connector.connect")
    @patch.dict("os.environ", {
        "host": "localhost",
        "database": "test_db",
        "user": "test_user",
        "password": "test_password"
    })
    def test_lambda_handler_success(self, mock_connect):
        """
        Test if the lambda function correctly retrieves data from the RDS 
        and processes it successfully.
        """
        # Mocking MySQL connection and cursor
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {
                "device_id": "device_001",
                "timestamp": "2022-10-12 12:00:00",
                "temperature": 25.0,
                "humidity": 50,
                "hvac_status": "on"
            }
        ]
        mock_connect.return_value = MagicMock(cursor=Mock(return_value=mock_cursor))

        # Sample test event for the lambda function
        event = {
            "device_id": "device_001",
            "date_range": {
                "start": "2022-10-01",
                "end": "2022-10-30"
            }
        }

        # Execute lambda handler with the test event
        response = retrieve_func.lambda_handler(event, None)

        # Asserts to verify correct behavior
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Data", json.loads(response["body"]))
        self.assertIn("Temperature Statistics", json.loads(response["body"]))
        self.assertIn("Humidity Statistics", json.loads(response["body"]))

        # Verify if SQL query execution was called on the mock cursor
        mock_cursor.execute.assert_called()


if __name__ == "__main__":
    unittest.main()
