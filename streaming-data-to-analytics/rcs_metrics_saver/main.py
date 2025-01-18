import base64
import json
import os
from google.cloud import bigquery
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def save_to_bq(envelop, context):
    """
    Triggered from a rcs message on a Pub/Sub topic.
    Inserts the message into BigQuery.
    """
    client = bigquery.Client()

    # Get environment variables
    dataset_id = os.environ.get('BQ_DATASET')
    rcs_request_count_type = os.environ.get('REQUEST_METRIC_TYPE')
    rcs_request_count_table_id = os.environ.get('REQUEST_BQ_TABLE')
    rcs_request_count_table_ref = client.dataset(dataset_id).table(rcs_request_count_table_id)

    rcs_final_response_count_table_id = os.environ.get('RESPONSE_BQ_TABLE')
    rcs_final_response_count_type = os.environ.get('RESPONSE_METRIC_TYPE')
    rcs_final_response_count_table_ref = client.dataset(dataset_id).table(rcs_final_response_count_table_id)

    # Extract data from the Pub/Sub message
    pubsub_message = base64.b64decode(envelop['data']).decode('utf-8')
    try:
        message_data = json.loads(pubsub_message)
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON: {pubsub_message}")
        return

    metric_type = message_data["metric"]["type"]
    metrics_labels = message_data["metric"]["labels"]
    conversation_type=metrics_labels.get("conversation_type","")
    carrier=metrics_labels.get("carrier","")
    sip_method=metrics_labels.get("sip_method","")
    response_code=metrics_labels.get("response_code","")
    direction=metrics_labels.get("direction","")
    start_time= message_data["points"][0]["interval"]["startTime"]
    end_time= message_data["points"][0]["interval"]["endTime"]
    value= message_data["points"][0]["value"]["int64Value"]
    
    # Prepare the row to be inserted
    row_to_insert = [
        {
            "metric_type" : metric_type,
            "conversation_type" : conversation_type,
            "carrier" : carrier,
            "sip_method" : sip_method,
            "response_code" : response_code,
            "direction" : direction,
            "start_time" : start_time,
            "end_time" : end_time,
            "value" : int(value)
        }
    ]

    # Insert data into BigQuery
    try:
        errors = None
        table_name = ""

        if metric_type == rcs_request_count_type:
            errors = client.insert_rows_json(rcs_request_count_table_ref, row_to_insert)
            table_name = rcs_request_count_table_ref.name
        elif metric_type == rcs_final_response_count_type:   
            errors = client.insert_rows_json(rcs_final_response_count_table_ref, row_to_insert)
            table_name = rcs_final_response_count_table_ref.name

        if errors:
            logger.error(f"Encountered errors while inserting rows: {errors}")
        else:
            logger.debug(f"Data inserted into BigQuery Table : {table_name}")
    except Exception as ex:
        logging.error(ex)
        traceback.print_exc()

    