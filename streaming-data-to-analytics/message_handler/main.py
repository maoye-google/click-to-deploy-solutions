import os
import json

from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["POST"])
def process_pubsub_message():
    """Receives and processes a Pub/Sub message."""

    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]

    try:
        # Decode the Pub/Sub message data (assuming it's base64 encoded)
        import base64

        message_data = base64.b64decode(
            pubsub_message["data"]
        ).decode() if "data" in pubsub_message else ""

        # You can also extract other attributes like messageId and publishTime if needed
        order_id = pubsub_message.get("order_id")
        publish_time = pubsub_message.get("publish_time")

        # Log the message content
        print(f"Received Order: id={order_id}, publish_time={publish_time}, data={message_data}")
        # Further processing or storing the message_data

        return "OK", 200

    except (ValueError, KeyError) as e:
        msg = f"error processing Pub/Sub message: {e}"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", "8080"))
    app.run(debug=True, host="0.0.0.0", port=PORT)