import os
import json
import base64
import logging
from flask import Flask, request
from google.cloud import pubsub_v1, monitoring_v3
from google.cloud.monitoring_v3.types import TimeSeries, TypedValue, Point, TimeInterval
from google.protobuf.json_format import MessageToDict, MessageToJson
from google.protobuf.timestamp_pb2 import Timestamp
import google.protobuf.json_format


# --- Constants for Cloud Monitoring ---
PROJECT_ID = os.getenv("PROJECT_ID")  # Get project ID from environment variable
# CLOUD_MONITORING_METRICS_NAME = os.getenv("CLOUD_MONITORING_METRICS_NAME") # get CLOUD_MONITORING_METRICS_NAME
# METRIC_TYPE = f"custom.googleapis.com/{CLOUD_MONITORING_METRICS_NAME}"  # User-defined metric type
# METRIC_KIND = ga_metric.MetricDescriptor.MetricKind.DELTA
# VALUE_TYPE = ga_metric.MetricDescriptor.ValueType.INT64
# ---------------------------------------

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

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


def send_metrics_to_stdio(data_list = {}):
    for data in data_list:
        msg = f"RCS Metrics Logging : {json.dumps(data)}"
        print(msg)
        logging.debug(msg)
        
    # print('Fishin running send_metrics_to_stdio !')
    # logging.debug(f"Fishin running send_metrics_to_stdio !")


def log_metrics_value(data_list = {}):
    # Synchrounous Scope
    
    # Option-1
    # Update Cloud Monitoring API to ingest the metrics
    # For this option, async task CANNOT be used. Otherwise you will receive error from the platform

    # send_metrics_to_cloud_monitoring(data)

    # Option-2
    # Send the Metrics to external Monitoring Tool like NewRelic or DataDog

    # option_2_task = asyncio.create_task(send_metrics_to_newrelic(data))
    # tasks.append(option_2_task)

    # Option-3
    # Send the Metrics to BigQuery

    # option_3_task = asyncio.create_task(send_metrics_to_bq(data))
    # tasks.append(option_3_task)

    # Option-4
    # Log the Metrics into Standard Output (can be tracked via Cloud Logging)

    send_metrics_to_stdio(data_list)



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
        # print('1')

        message_data = base64.b64decode(
            pubsub_message["data"]
        ).decode() if "data" in pubsub_message else ""

        # print('2')
        
        # You can also extract other attributes like messageId and publishTime if needed
        publish_time = pubsub_message.get("publish_time")
        
        # Ready to parse Message Body
        request_data = json.loads(message_data)

        # print('3')
        
        print(request_data)
        # t=request_data["timeSeries"]
        # time_series_list = extract_time_series(t)
        data_list = []

        print('4')
        
        # for time_series in time_series_list:
        #     print('5')
        metric_type = request_data["metric"]["type"]
        metrics_labels = request_data["metric"]["labels"]
        conversation_type=metrics_labels.get("conversation_type","")
        carrier=metrics_labels.get("carrier","")
        sip_method=metrics_labels.get("sip_method","")
        response_code=metrics_labels.get("response_code","")
        direction=metrics_labels.get("direction","")
        value= request_data["points"][0]["value"]["int64Value"]

        print('6')
            
        data = {
            metric_type : metric_type,
            conversation_type : conversation_type,
            carrier : carrier,
            sip_method : sip_method,
            response_code : response_code,
            direction : direction,
            value : value
        }

        data_list.append(data)

        print('7')
        
        log_metrics_value(data_list) 

        logging.info(f"Finish process RCS Metrics")

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
