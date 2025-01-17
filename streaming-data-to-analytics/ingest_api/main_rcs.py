import http
import os
import logging
import json
from wsgiref import validate
from flask import Flask, request, jsonify

from google.cloud import pubsub_v1, monitoring_v3
from google.cloud.monitoring_v3.types import TimeSeries, TypedValue, Point, TimeInterval
from google.protobuf.json_format import MessageToDict, MessageToJson
from google.protobuf.timestamp_pb2 import Timestamp
import google.protobuf.json_format



PROJECT_ID = os.getenv("PROJECT_ID")  # Get project ID from environment variable
TOPIC_ID = os.environ.get("TOPIC_ID")

app = Flask(__name__)

def create_timeseries_request_modal(ts_data=None):
    if (ts_data is None):
        print(f"Empty Result")
        return None
    # print("Step 12")
    time_series = TimeSeries()

    # print("Step 13")
    # Required Fields: metric, resource, metric_kind, value_type
    time_series.metric.type = ts_data.get("metric", {}).get("type")
    # print(time_series.metric.type)

    # print("Step 14")
    for label_key, label_value in ts_data.get("metric", {}).get("labels", {}).items():
        time_series.metric.labels[label_key] = label_value

    # print("Step 15")
    for point_data in ts_data.get("points", []):
        point = Point()
        interval = TimeInterval()

        # print("Step 15.1 Start")
        start_time = Timestamp()
        start_time.FromJsonString(point_data.get("interval", {}).get("startTime"))
        interval.start_time = start_time

        # print("Step 15.2 Start")
        end_time = Timestamp()
        end_time.FromJsonString(point_data.get("interval", {}).get("endTime"))
        interval.end_time = end_time

        # print("Step 15.3 Start")
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

        # print("Step 15.4 Start")
        point.value = value
        time_series.points.append(point)

    return time_series
    
def extract_time_series(json_list=None):
    time_series_list = []
    if (json_list is None):
        print(f"Empty List")
        return None
    # print(json_list)
    for ts_data in json_list:
        modal = create_timeseries_request_modal(ts_data)
        if (modal is not None):
            time_series_list.append(modal)

    return time_series_list

@app.route("/rcs-metrics", methods=['POST'])
def publish_rcs_metrics():
    """
    Receives a POST request with a JSON payload representing a CreateTimeSeriesRequest
    and deserializes it into a proto object.
    """
    try:
        # print("-1")
        request_data = request.get_json()
        # print(request_data)
        t=request_data["timeSeries"]
        # print("-2")
        time_series_list = extract_time_series(t)
        # print("-3")
        placeholder = monitoring_v3.CreateTimeSeriesRequest(
            name=request_data["name"],
            time_series=time_series_list
        )
        # print("-4")
        # print(MessageToDict(placeholder._pb))
        for timeseries_data in time_series_list:
            # Publish the message to Pub/sub
            # print(timeseries_data)
            print("-5")
            metric_type = timeseries_data.metric.type
            print("-6")
            message = MessageToDict(timeseries_data._pb)
            print(message)

        return jsonify({'message': 'CreateTimeSeriesRequest received successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
