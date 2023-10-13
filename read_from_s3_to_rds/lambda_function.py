import json
import boto3
import csv
import mysql.connector
import os

# Create an S3 client
s3_client = boto3.client('s3')


def clean_data(row):
    """
    Cleans and validates a single row of data.

    Parameters:
    - row (dict): The row to be cleaned and validated.

    Returns:
    - tuple: Cleaned values for device_id, timestamp, temperature, humidity, hvac_status.
    """
    # Clean and validate device_id
    device_id = str(row['device_id']).strip()

    # Clean and validate timestamp
    try:
        timestamp = str(row['timestamp']).strip()
    except ValueError:
        timestamp = None

    # Clean and validate temperature
    try:
        temperature = float(row['temperature'])
        if not (0 <= temperature <= 50):
            temperature = None
    except ValueError:
        temperature = None

    # Clean and validate humidity
    try:
        humidity = float(row['humidity'])
        if not (0 <= humidity <= 100):
            humidity = None
    except ValueError:
        humidity = None

    # Clean and validate hvac_status
    hvac_status = str(row['hvac_status']).lower().strip()
    if hvac_status not in ['on', 'off']:
        hvac_status = None

    return device_id, timestamp, temperature, humidity, hvac_status


def lambda_handler(event, context):
    """
    AWS Lambda function handler to process the given event.

    Parameters:
    - event (dict): The AWS Lambda event to be processed.
    - context (object): AWS Lambda context object.

    Returns:
    - dict: Dictionary with statusCode and body for the response.
    """
    try:
        print(f"Received event: {json.dumps(event)}")

        records = event.get('Records')
        if not records:
            return {
                'statusCode': 400,
                'body': json.dumps('Event does not contain Records.')
            }

        bucket = records[0].get('s3', {}).get('bucket', {}).get('name')
        txt_file = records[0].get('s3', {}).get('object', {}).get('key')

        if not bucket or not txt_file:
            return {
                'statusCode': 400,
                'body': json.dumps('Could not retrieve bucket or file key from event.')
            }

        txt_file_object = s3_client.get_object(Bucket=bucket, Key=txt_file)
        lines = txt_file_object['Body'].read().decode('utf-8').splitlines()

        if not lines:
            return {
                'statusCode': 400,
                'body': json.dumps('No data in the file.')
            }

        results = []
        for row in csv.DictReader(lines):
            cleaned_data = clean_data(row)
            if None not in cleaned_data:
                results.append(cleaned_data)
            else:
                print(f"Skipped invalid data: {row}")

        # Connect to the database
        connection = mysql.connector.connect(
            host=os.environ['host'],
            database=os.environ['database'],
            user=os.environ['user'],
            password=os.environ['password']
        )

        try:
            cursor = connection.cursor()
            insert_query = (
                "INSERT INTO iot_device_data "
                "(device_id, timestamp, temperature, humidity, hvac_status) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            cursor.executemany(insert_query, results)
            connection.commit()
            print(f"Processed {cursor.rowcount} rows from the text file!")
        finally:
            cursor.close()
            connection.close()

        return {
            'statusCode': 200,
            'body': json.dumps('success!')
        }

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Database error: {err}")
        }

    except Exception as e:
        print(f"General error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"An error occurred: {e}")
        }
