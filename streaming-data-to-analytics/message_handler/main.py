import os
import json
import base64
import logging

from flask import Flask, request


# --- Constants for Cloud Monitoring ---
PROJECT_ID = os.getenv("PROJECT_ID")  # Get project ID from environment variable
# CLOUD_MONITORING_METRICS_NAME = os.getenv("CLOUD_MONITORING_METRICS_NAME") # get CLOUD_MONITORING_METRICS_NAME
# METRIC_TYPE = f"custom.googleapis.com/{CLOUD_MONITORING_METRICS_NAME}"  # User-defined metric type
# METRIC_KIND = ga_metric.MetricDescriptor.MetricKind.DELTA
# VALUE_TYPE = ga_metric.MetricDescriptor.ValueType.INT64
# ---------------------------------------

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)


@app.route("/", methods=["POST"])
def process_pubsub_message():
    """Receives and processes a Pub/Sub message."""

    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        logging.error(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        logging.error(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]

    try:
        # Decode the Pub/Sub message data (assuming it's base64 encoded)
        import base64

        message_data = base64.b64decode(
            pubsub_message["data"]
        ).decode() if "data" in pubsub_message else ""
        # You can also extract other attributes like messageId and publishTime if needed
        publish_time = pubsub_message.get("publish_time")
        
        # Ready to parse Message Body
        message_data = json.loads(message_data)

        order_id = message_data.get("order_id")
        customer_email = message_data.get("customer_email")
        phone_number = message_data.get("phone_number")
        action = message_data.get("action")

        # Log the message content
        msg = f"Received Order: order_id={order_id}, publish_time={publish_time}, customer_email={customer_email}, phone_number={phone_number}, action={action}"
        # print(msg)
        logging.info(msg)

        return "OK", 200

    except (ValueError, KeyError) as e:
        msg = f"error processing Pub/Sub message: {e}"
        logging.error(f"error: {msg}")
        return f"Bad Request: {msg}", 400

if __name__ == "__main__":
    # Create the custom metric descriptor before starting the app
    # create_custom_metric()

    PORT = int(os.getenv("PORT", "8080"))
    app.run(debug=True, host="0.0.0.0", port=PORT)