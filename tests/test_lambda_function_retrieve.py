# tests/test_lambda_function_retrieve.py

import unittest
from unittest.mock import patch, Mock, MagicMock
from read_from_rds import lambda_function as retrieve_func
import json


class TestLambdaFunctionRetrieve(unittest.TestCase):

    @patch("mysql.connector.connect")
    @patch.dict("os.environ", {
        "host": "localhost",
        "database": "test_db",
        "user": "test_user",
        "password": "test_password"
    })
    def test_lambda_handler_success(self, mock_connect):
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

        # Test event
        event = {
            "device_id": "device_001",
            "date_range": {
                "start": "2022-10-01",
                "end": "2022-10-30"
            }
        }

        response = retrieve_func.lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Data", json.loads(response["body"]))
        self.assertIn("Temperature Statistics", json.loads(response["body"]))
        self.assertIn("Humidity Statistics", json.loads(response["body"]))
        mock_cursor.execute.assert_called()

    # Again, you can add more tests for various scenarios.


if __name__ == "__main__":
    unittest.main()
