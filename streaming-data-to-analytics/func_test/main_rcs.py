import os
import json
import requests
import logging
from urllib.parse import urljoin
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import google.auth.transport.requests
import google.oauth2.id_token
import time
import uuid
import random
from random import randrange
from faker import Faker
from google.cloud import monitoring_v3
from google.cloud.monitoring_v3.types import TimeSeries, TypedValue, Point, TimeInterval
from google.protobuf.timestamp_pb2 import Timestamp
import google.protobuf.json_format
from google.protobuf.json_format import MessageToDict, MessageToJson

logger = logging.getLogger(__name__)

def serialize_timeseries(request_payload = None):
    try:
        # request_proto = json_format.Parse(
        #     json_string.decode('utf-8'), monitoring_v3.CreateTimeSeriesRequest()
        # )

        str_ret=MessageToDict(request_payload._pb)
        print("CreateTimeSeriesRequest serialized successfully")
        return str_ret

    except requests.exceptions.RequestException as e:
        print(f"Error Serializing CreateTimeSeriesRequest to String : {e}")

def create_timeseries_request_modal(ts_data=None):
    if (ts_data is None):
        print(f"Empty Result")
        return None
    
    time_series = TimeSeries()
    
    # Required Fields: metric, resource, metric_kind, value_type
    time_series.metric.type = ts_data.get("metric", {}).get("type")
    # print(time_series.metric.type)

    for label_key, label_value in ts_data.get("metric", {}).get("labels", {}).items():
        time_series.metric.labels[label_key] = label_value

    for point_data in ts_data.get("points", []):
        point = Point()
        interval = TimeInterval()

        # print("Step4.x Start")
        start_time = Timestamp()
        start_time.FromJsonString(point_data.get("interval", {}).get("startTime"))
        interval.start_time = start_time
        
        end_time = Timestamp()
        end_time.FromJsonString(point_data.get("interval", {}).get("endTime"))
        interval.end_time = end_time

        point.interval = interval

        value = TypedValue()

        value_tuple = point_data.get("value",{})
        if "int64Value" in value_tuple:
            # For RCS Metrics, the value will always be int64
            value.int64_value = int(value_tuple["int64Value"])
        elif "doubleValue" in value_tuple:
            value.double_value = float(value_tuple["doubleValue"])
        elif "stringValue" in value_tuple:
            value.string_value = value_tuple["stringValue"]
        elif "boolValue" in value_tuple:
            value.bool_value = bool(value_tuple["boolValue"])

        point.value = value
        time_series.points.append(point)

    return time_series

def load_timeseries_payload_from_file(json_file_path):
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        time_series_list = []
        for ts_data in data:
            modal = create_timeseries_request_modal(ts_data)
            if (modal is not None):
               time_series_list.append(modal)

        return time_series_list
    
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error loading TimeSeries from JSON: {e}")
        return None
        
def post_to_cloud_run(service_url, relative_path,service_account_key_path, data, audience=None):
    """
    Sends a POST request to a Cloud Run service that requires authentication.

    Args:
        service_url: The URL of the Cloud Run service.
        service_account_key_path: Path to the service account key file (JSON).
        data: A dictionary containing the data to be sent in the POST request body.
        audience: (Optional) Audience for the ID token, defaults to the service URL.
    """

    # 1. Set the GOOGLE_APPLICATION_CREDENTIALS environment variable.
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_key_path

    # 2. Determine the audience (use base URL as audience).
    if audience is None:
        audience = service_url

    # 3. Construct the full URL with the relative path.
    full_url = urljoin(service_url, relative_path)

    # 4. Create a request object with automatic token refresh.
    request = google.auth.transport.requests.Request()

    # 5. Generate the ID token.
    try:
        id_token = google.oauth2.id_token.fetch_id_token(request, audience)
    except Exception as e:
        print(f"Error fetching ID token: {e}")
        return

    # 6. Prepare the headers for the request.
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json",  # Specify JSON content type
    }

    # 7. Make the POST request to the Cloud Run service.
    try:
        # print(data)
        response = requests.post(full_url, headers=headers, json=data)  # Send data as JSON
        response.raise_for_status()

        print(f"Successfully posted data to Cloud Run service: {full_url}")
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error posting data to Cloud Run service: {e}")



def main():
    """
    Main function to demonstrate posting data to Cloud Run with JSON key authentication.
    """
    cloud_run_url = os.environ.get("CLOUD_RUN_ENDPOINT")
    # sa_email = os.environ.get("SA_NAME")  # Replace with your service account email
    # print(f"Finish loading SA Name : {sa_email}")

    # --- Option 1: Service Account Key from Environment Variable (Recommended) ---
    service_account_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    # --- Option 2: Hardcoded Service Account Key Path (Less Secure) ---
    # service_account_path = "/path/to/your/service-account-key.json"

    # --- Option 3: Application Default Credentials (ADC) ---
    # If you want to use ADC, comment out the above two options.

    if not service_account_path:
        print("Warning: Service account key path not set. Attempting to use ADC.")

    # Option-2 : Load data from JSON payload file

    relative_path = "/rcs-metrics"
    data = load_timeseries_payload_from_file("./sample_payload.json")

    request_payload = monitoring_v3.CreateTimeSeriesRequest(
        name='PROJECT_ID', time_series=data)
    
    json = serialize_timeseries(request_payload)

    response = post_to_cloud_run(
            cloud_run_url,
            relative_path,
            service_account_path,
            data=json
        )


if __name__ == "__main__":
    main()
