resource "google_cloudfunctions2_function" "save_rcs_metrics_to_bigquery" {
  name        = "save-rcs-metrics-to-bigquery"
  description = "Subscribes RCS Metrics from Pub/Sub, and inserts into BigQuery"
  location      = var.region # Choose your desired region

  build_config {
    runtime = "python39"
    entry_point = "save_to_bq"  # Set the entry point 
    source {
      storage_source {
        bucket = google_storage_bucket.cloudfunctions_tmp_bucket.name
        object = var.rcs_metrics_saver_cf_zip_name
      }
    }
  }

  service_config {
    max_instance_count  = 2
    available_memory    = "256M"
    timeout_seconds     = 60

    environment_variables = {
        BQ_DATASET = google_bigquery_table.rcs_metrics_request_count.dataset_id # Replace with your BigQuery dataset
        REQUEST_METRIC_TYPE = local.res_request_count_metrics_type
        REQUEST_BQ_TABLE   = google_bigquery_table.rcs_metrics_request_count.table_id  # Replace with your BigQuery table
        RESPONSE_METRIC_TYPE = local.res_final_response_count_metrics_type
        RESPONSE_BQ_TABLE   = google_bigquery_table.rcs_metrics_final_response_count.table_id  # Replace with your BigQuery table
    }
    ingress_settings = "ALLOW_INTERNAL_ONLY"
    all_traffic_on_latest_revision = true
    service_account_email = google_service_account.ingest_api.email
  }

  event_trigger {
    trigger_region = var.region
    event_type = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = google_pubsub_topic.rcs_topic.name
    retry_policy = "RETRY_POLICY_RETRY"
  }
}