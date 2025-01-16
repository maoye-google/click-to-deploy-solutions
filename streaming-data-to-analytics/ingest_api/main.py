import http
import os
import logging

from wsgiref import validate
from flask import Flask, request, jsonify

from google.cloud import pubsub_v1
from google.cloud.monitoring_v3.types import TimeSeries, TypedValue, Point, Interval
from google.protobuf.timestamp_pb2 import Timestamp



PROJECT_ID = os.getenv("PROJECT_ID")  # Get project ID from environment variable
TOPIC_ID = os.environ.get("TOPIC_ID")

app = Flask(__name__)


def map_json_to_timeseries(json_data):
    """Maps JSON data to a list of TimeSeries objects.

    Args:
        json_data: The JSON data (list of dictionaries).

    Returns:
        A list of TimeSeries objects, or None if an error occurs.
    """
    try:
        time_series_list = []
        for ts_data in json_data:
            time_series = TimeSeries()

            time_series.metric.type = ts_data.get("metric", {}).get("type")
            for label_key, label_value in ts_data.get("metric", {}).get("labels", {}).items():
                time_series.metric.labels[label_key] = label_value

            time_series.resource.type = ts_data.get("resource", {}).get("type")
            for label_key, label_value in ts_data.get("resource", {}).get("labels", {}).items():
                time_series.resource.labels[label_key] = label_value

            time_series.metric_kind = ts_data.get("metricKind")
            time_series.value_type = ts_data.get("valueType")

            for point_data in ts_data.get("points", []):
                point = Point()
                interval = Interval()

                start_time = Timestamp()
                start_time.FromJsonString(point_data.get("interval", {}).get("startTime"))
                interval.start_time = start_time

                end_time = Timestamp()
                end_time.FromJsonString(point_data.get("interval", {}).get("endTime"))
                interval.end_time = end_time

                point.interval = interval

                value = TypedValue()
                value_type = time_series.value_type
                if value_type == "INT64":
                    value.int64_value = int(point_data.get("value", {}).get("int64Value"))
                elif value_type == "DOUBLE":
                    value.double_value = float(point_data.get("value", {}).get("doubleValue"))
                elif value_type == "STRING":
                    value.string_value = point_data.get("value", {}).get("stringValue")
                elif value_type == "BOOL":
                    value.bool_value = bool(point_data.get("value", {}).get("boolValue"))
                # Add other types as needed (DISTRIBUTION, etc.)
                point.value = value
                time_series.points.append(point)

            time_series_list.append(time_series)

        return time_series_list

    except (KeyError, TypeError, ValueError) as e:  # Catch Value Error for invalid JSON
        print(f"Error mapping JSON to TimeSeries: {e}")
        return None
    

@app.route("/", methods=['GET'])
def hello():
    return 'hello'

def extract_data_from_metrics(timeseries_data = None):
    # Extract data from fields
    conversation_type = timeseries_data.metric.labels['conversation_type']
    carrier = timeseries_data.metric.labels['carrier']
    sip_method = timeseries_data.metric.labels['sip_method']
    response_code = timeseries_data.metric.labels['response_code'] or ""
    direction = timeseries_data.metric.labels['direction']
    point_data = timeseries_data.points[0]
    start_time = point_data.interval.start_time
    end_time = point_data.interval.end_time
    value = point_data.value

    # compose and return simplied JSON object
    return {
        "conversation_type" : conversation_type,
        "carrier" : carrier,
        "sip_method" : sip_method,
        "response_code" : response_code,
        "direction":direction,
        "start_time":start_time,
        "end_time":end_time,
        "value":value
    }

@app.route("/rcs-metrics", methods=['POST'])
def publish():
    try:
        # Request validation
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        # Get the request data
        json_data = request.get_json()

        if not isinstance(json_data, list): # Check for a list
            return jsonify({"error": "Request body must be a JSON list of TimeSeries"}), 400
        
        timeseries_data_list = map_json_to_timeseries(json_data)

        if timeseries_data_list is None:
            return jsonify({"error": "Invalid TimeSeries data in request"}), 400
        

        # Pub/sub publisher
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

        for timeseries_data in timeseries_data_list:
            # Publish the message to Pub/sub
            metric_type = timeseries_data.metric.type
            data = extract_data_from_metrics(timeseries_data)
        
            publisher.publish(topic_path, 
                              data, 
                              metric_type=metric_type,
                            #   conversation_type=data["conversation_type"],
                            #   carrier=data["carrier"],
                            #   sip_method=data["sip_method"],
                            #   response_code=data["response_code"],
                            #   direction=data["direction"]
                              )
        
        logging.info(f"Published {len(timeseries_data_list)} RCS metrics of Type ({metric_type})")

    except Exception as ex:
        logging.error(ex)
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
