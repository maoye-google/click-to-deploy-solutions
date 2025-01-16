import os
import json
import requests
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

def create_json_payload():
    fake = Faker()
    actions = ["created", "cancelled", "updated", "delivered"]
    order = {
        "order_id": str(uuid.uuid1()),
        "customer_email": fake.free_email(),
        "phone_number": fake.phone_number(),
        "user_agent": fake.chrome(),
        "action": random.choice(actions),
        "action_time": int(time.time())
    }
    data = order;
    return data


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

    # Data to send
    data = create_json_payload()

    relative_path = "/?entity=order-event"
    response = post_to_cloud_run(
            cloud_run_url,
            relative_path,
            service_account_path,
            data=data
        )


if __name__ == "__main__":
    main()
