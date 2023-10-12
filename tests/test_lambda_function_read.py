# tests/test_lambda_function_read.py

import unittest
from unittest.mock import patch, Mock
import lambda_function_read as read
from unittest import TestCase, mock
from read_from_s3_to_rds import lambda_function
import json
import os

class TestLambdaFunctionRead(unittest.TestCase):
    
    @mock.patch("lambda_function_read.mysql.connector.connect")
    @mock.patch("lambda_function_read.s3_client.get_object")
    @mock.patch.dict(os.environ, {
    'host': 'mocked_host',
    'database': 'mocked_database',
    'user': 'mocked_user',
    'password': 'mocked_password'
})
    def test_lambda_handler_success(self, mock_get_object, mock_db_connect):
        
        mock_body_content = "device_id,timestamp,temperature,humidity,hvac_status\n1,2022-10-12 00:00:00,25,50,on"
        mock_get_object.return_value = {
            "Body": mock.MagicMock(read=lambda: mock_body_content.encode('utf-8'))
        }


        # Set up the mock for the mysql connection and cursor
        mock_connection = mock_db_connect.return_value
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.rowcount = 1
        
        # Prepare the event for testing
        event = {
            "Records": [{
                "s3": {
                    "bucket": {"name": "test_bucket"},
                    "object": {"key": "test_key.txt"}
                }
            }]
        }
        
        # Call the lambda_handler function
        response = lambda_function.lambda_handler(event, {})
        
        # Validate the response
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], json.dumps('success!'))



    @patch("lambda_function_read.boto3.client")
    def test_lambda_handler_no_records(self, mock_s3):
        event = {}
        response = read.lambda_function.lambda_handler(event, None)

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(response["body"], '"Event does not contain Records."')


if __name__ == "__main__":
    unittest.main()
