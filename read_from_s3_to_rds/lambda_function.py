import json
import boto3
import csv
import mysql.connector
import os

s3_client = boto3.client('s3')


def clean_data(row):
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
        if not (0 <= temperature <= 50):  # example range, adjust as needed
            temperature = None
    except ValueError:
        temperature = None

    # Clean and validate humidity
    try:
        humidity = float(row['humidity'])
        if not (0 <= humidity <= 100):  # range: 0-100%
            humidity = None
    except ValueError:
        humidity = None

    # Clean and validate hvac_status
    hvac_status = str(row['hvac_status']).lower().strip()
    if hvac_status not in ['on', 'off']:
        hvac_status = None

    return device_id, timestamp, temperature, humidity, hvac_status


def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

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

        connection = mysql.connector.connect(
            host=os.environ['host'],
            database=os.environ['database'],
            user=os.environ['user'],
            password=os.environ['password']
        )

        try:
            cursor = connection.cursor()
            insert_query = ("INSERT INTO iot_device_data "
                            "(device_id, timestamp, temperature, humidity, hvac_status) "
                            "VALUES (%s, %s, %s, %s, %s)")
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
        print("Database error:", err)
        return {
            'statusCode': 500,
            'body': json.dumps(f"Database error: {err}")
        }

    except Exception as e:
        print("General error:", e)
        return {
            'statusCode': 500,
            'body': json.dumps(f"An error occurred: {e}")
        }