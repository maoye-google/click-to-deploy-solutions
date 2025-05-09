import base64
import json
import os
from google.cloud import bigquery
import logging
import traceback
import functions_framework

@functions_framework.cloud_event
def save_to_bq(request):
    """
    Triggered from a rcs message on a Pub/Sub topic.
    Inserts the message into BigQuery.
    """
    PROJECT_ID = os.getenv("PROJECT_ID") 
    client = bigquery.Client(project=PROJECT_ID)

    # Get environment variables
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    dataset_id = os.environ.get('BQ_DATASET')
    table_id = os.environ.get('BQ_TABLE')

    logger.debug(f"table_id is {table_id}")
    _rcs_metrics_all_table_ref = client.dataset(dataset_id).table(table_id)
    rcs_metrics_all_table = client.get_table(_rcs_metrics_all_table_ref)

    logger.debug(f"Finish Cloud Function Initialization")

    # Read pub sub data 
    envelope = request.get_data()
    if not envelope:
        msg = "no Pub/Sub message received"
        logger.error(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        logger.error(f"error: {msg}")
        logger.debug(f"received message is : {envelope}")
        return f"Bad Request: {msg}", 400

    # Extract data from the Pub/Sub message
    
    try:
        pubsub_message = envelope["message"]

        message_data = base64.b64decode(
            pubsub_message["data"]
        ).decode() if "data" in pubsub_message else ""
        message_data = json.loads(message_data)
    
        # Parse Message Data
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

        logger.debug(f"Finish Parsing the received message = {message_data}")
        
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
    
        errors = client.insert_rows_json(rcs_metrics_all_table, row_to_insert)
        
        if errors:
            msg = f"Encountered errors while inserting rows: {errors}"
            logger.error(msg)
            return msg, 400
        else:
            msg = f"Data inserted into BigQuery Table : {table_id}"
            logger.debug(msg)
            return msg, 200
        
    except Exception as ex:
        logging.error(ex)
        traceback.print_exc()
        return "Error", 400