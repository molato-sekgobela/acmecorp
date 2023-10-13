import unittest
from unittest.mock import patch, Mock
from read_from_s3_to_rds import lambda_function as read
from unittest import TestCase, mock
from read_from_s3_to_rds import lambda_function
import json
import os


class TestLambdaFunctionRead(unittest.TestCase):
    """
    Test cases for the lambda function that reads data from S3 and writes to RDS.
    """

    @mock.patch("lambda_function_read.mysql.connector.connect")
    @mock.patch("lambda_function_read.s3_client.get_object")
    @mock.patch.dict(os.environ, {
        'host': 'mocked_host',
        'database': 'mocked_database',
        'user': 'mocked_user',
        'password': 'mocked_password'
    })
    def test_lambda_handler_success(self, mock_get_object, mock_db_connect):
        """
        Test if the lambda function correctly reads data from S3 and writes to RDS.
        """
        # Mock S3 object content
        mock_body_content = "device_id,timestamp,temperature,humidity,hvac_status\n1,2022-10-12 00:00:00,25,50,on"
        mock_get_object.return_value = {
            "Body": mock.MagicMock(read=lambda: mock_body_content.encode('utf-8'))
        }

        # Mock the MySQL connection and cursor
        mock_connection = mock_db_connect.return_value
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.rowcount = 1

        # Sample test event for the lambda function
        event = {
            "Records": [{
                "s3": {
                    "bucket": {"name": "test_bucket"},
                    "object": {"key": "test_key.txt"}
                }
            }]
        }

        # Execute lambda_handler with the test event
        response = lambda_function.lambda_handler(event, {})

        # Asserts to verify correct behavior
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], json.dumps('success!'))

    @patch("lambda_function_read.boto3.client")
    def test_lambda_handler_no_records(self, mock_s3):
        """
        Test the behavior of the lambda function when there are no S3 records.
        """
        event = {}
        response = read.lambda_function.lambda_handler(event, None)

        # Asserts to verify correct behavior
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(response["body"], '"Event does not contain Records."')


if __name__ == "__main__":
    unittest.main()
