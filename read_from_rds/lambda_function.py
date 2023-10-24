import json
import mysql.connector
import os
import statistics
import datetime


class DateTimeEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for datetime objects.
    Converts datetime objects into string format.
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super(DateTimeEncoder, self).default(obj)


def retrieve_data(device_id, start_date, end_date):
    """
    Retrieves data from the MySQL database for a given device_id within a specified date range.

    Parameters:
    - device_id (str): ID of the device.
    - start_date (str): Start date for data retrieval.
    - end_date (str): End date for data retrieval.

    Returns:
    - list: List of dictionaries containing data for the specified device and date range.
    """
    # Connect to the MySQL database
    connection = mysql.connector.connect(
        host=os.environ['host'],
        database=os.environ['database'],
        user=os.environ['user'],
        password=os.environ['password']
    )
    cursor = connection.cursor(dictionary=True)

    # Execute query
    query = ("SELECT device_id,timestamp,temperature,humidity FROM iot_device_data "
             "WHERE device_id = %s AND timestamp BETWEEN %s AND %s")
    cursor.execute(query, (device_id, start_date, end_date))

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results


def compute_statistics(data, column_name):
    """
    Computes basic statistics (mean, median, min, max) for a given column in the data.

    Parameters:
    - data (list): List of dictionaries containing the data.
    - column_name (str): Name of the column for which statistics will be computed.

    Returns:
    - dict: Dictionary containing the computed statistics.
    """
    values = [row[column_name] for row in data if row[column_name] is not None]
    if not values:
        return None

    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values)
    }


def lambda_handler(event, context):
    """
    AWS Lambda function handler to process the given event.

    Parameters:
    - event (dict): The AWS Lambda event to be processed.
    - context (object): AWS Lambda context object.

    Returns:
    - dict: Dictionary with statusCode and body for the response.
    """
    device_id = event.get('device_id')
    date_range = event.get('date_range')

    if not device_id or not date_range:
        return {
            'statusCode': 400,
            'body': json.dumps('device_id and date_range are required.')
        }

    data = retrieve_data(device_id, date_range['start'], date_range['end'])

    temperature_stats = compute_statistics(data, 'temperature')
    humidity_stats = compute_statistics(data, 'humidity')

    # Format the retrieved data for output
    formatted_data = [
        f"Device ID: {entry['device_id']}, Timestamp: {entry['timestamp']}, Temperature: {entry['temperature']}°C, "
        f"Humidity: {entry['humidity']}%, HVAC Status: {entry['hvac_status']}"
        for entry in data
    ]

    # Format the statistics for output
    if temperature_stats:
        formatted_temperature_stats = (
            f"Temperature - Mean: {temperature_stats['mean']}°C, Median: {temperature_stats['median']}°C, "
            f"Min: {temperature_stats['min']}°C, Max: {temperature_stats['max']}°C"
        )
    else:
        formatted_temperature_stats = "Temperature data not available"

    if humidity_stats:
        formatted_humidity_stats = (
            f"Humidity - Mean: {humidity_stats['mean']}%, Median: {humidity_stats['median']}%, "
            f"Min: {humidity_stats['min']}%, Max: {humidity_stats['max']}%"
        )
    else:
        formatted_humidity_stats = "Humidity data not available"

    response = {
        'Data': formatted_data,
        'Temperature Statistics': formatted_temperature_stats,
        'Humidity Statistics': formatted_humidity_stats
    }

    return {
        'statusCode': 200,
        'body': json.dumps(response, cls=DateTimeEncoder)
    }
