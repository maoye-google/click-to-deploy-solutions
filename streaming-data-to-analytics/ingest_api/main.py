import http
import os
import logging
import json
from wsgiref import validate
from flask import Flask, request, jsonify

from google.cloud import pubsub_v1, monitoring_v3
from google.protobuf.timestamp_pb2 import Timestamp
import google.protobuf.json_format



PROJECT_ID = os.getenv("PROJECT_ID")  # Get project ID from environment variable
TOPIC_ID = os.environ.get("TOPIC_ID")

app = Flask(__name__)

def extract_data_from_metrics(timeseries_data = None):
    # Extract data from fields
    metric_labels = timeseries_data["metric"]["labels"]
    conversation_type = metric_labels['conversation_type']
    carrier = metric_labels['carrier']
    sip_method = metric_labels['sip_method']
    response_code = ""
    if "response_code" in metric_labels:
        response_code = metric_labels['response_code']
    direction = metric_labels['direction']

    point_data = timeseries_data["points"][0]
    start_time = point_data["interval"]["startTime"]
    end_time = point_data["interval"]["endTime"]
    value = point_data["value"]['int64Value']

    # compose and return simplied JSON object
    return {
        "conversation_type" : conversation_type,
        "carrier" : carrier,
        "sip_method" : sip_method,
        "response_code" : response_code,
        "direction":direction,
        "start_time":start_time,
        "end_time":end_time,
        "value":int(value)
    }


@app.route("/", methods=['GET'], endpoint="hello")
def hello():
    return 'hello'

@app.route("/rcs-metrics", methods=['POST'])
def publish_rcs_metrics():
    try:
        data = request.get_data()
        # print(data)
        print("Step1")
        request_payload = json.loads(data)
        timeseries_data_list = request_payload["timeSeries"]
        print("Step2")
        if timeseries_data_list is None:
            return jsonify({"error": "Invalid TimeSeries data in request"}), 400
        print("Step3")

        # Pub/sub publisher
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
        print("Step4")

        for timeseries_data in timeseries_data_list:
            # Publish the message to Pub/sub
            # print(timeseries_data)
            print("Step5")
            metric_type = timeseries_data["metric"]["type"]
            print("Step6")
            message = extract_data_from_metrics(timeseries_data)
            print("Step7")
            publisher.publish(topic_path, 
                              json.dumps(message).encode("utf-8"), 
                              metric_type=metric_type,
                            #   conversation_type=data["conversation_type"],
                            #   carrier=data["carrier"],
                            #   sip_method=data["sip_method"],
                            #   response_code=data["response_code"],
                            #   direction=data["direction"]
                            )
        # print("Step4")
        logging.info(f"Published {len(timeseries_data_list)} RCS metrics of Type ({metric_type})")

    except Exception as ex:
        logging.error(ex)
        # print("Step5")
        return 'error:{}'.format(ex), http.HTTPStatus.INTERNAL_SERVER_ERROR

    return 'success'

@app.route("/", methods=['POST'])
def publish():
    try:
        # Request validation
        args = request.args
        entity = args.get("entity")
        if not entity:
            entity = "unknown"

        # Get the request data
        data = request.get_data()
        
        # TO-DO - If you need to validate the request, add your code here

        # Pub/sub publisher
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
        
        # Publish the message to Pub/sub
        publisher.publish(topic_path, data, entity=entity)
    except Exception as ex:
        logging.error(ex)
        return 'error:{}'.format(ex), http.HTTPStatus.INTERNAL_SERVER_ERROR

    return 'success'


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
