resource "google_pubsub_topic" "ingest_api" {
  name   = "ingest-api"
  labels = local.resource_labels
}

# ######################################################################

# Forward RCS Time Series Metrics (Request Count) to BQ via Pub/Sub
resource "google_pubsub_subscription" "rcs_timeseris_request_count_to_bq_sub" {
  name   = "rcs-timeseries-request-count-to-bigquery"
  topic  = google_pubsub_topic.ingest_api.name
  labels = local.resource_labels
  filter = "attributes.entity=\"custom.googleapis.com/rcs/sip/request_count\""

  bigquery_config {
    table          = "${google_bigquery_table.rcs_timeseris.project}.${google_bigquery_table.rcs_timeseris.dataset_id}.${google_bigquery_table.rcs_timeseris.request_count_table_id}"
    write_metadata = true
  }

  depends_on = [
    google_project_iam_member.pubsub_bqEditor,
    google_project_iam_member.pubsub_bqMetadata
  ]
}

# Forward RCS Time Series Metrics (Final Response Count) to BQ via Pub/Sub
resource "google_pubsub_subscription" "rcs_timeseris_final_response_count_to_bq_sub" {
  name   = "rcs-timeseries-final-response-count-to-bigquery"
  topic  = google_pubsub_topic.ingest_api.name
  labels = local.resource_labels
  filter = "attributes.entity=\"custom.googleapis.com/rcs/sip/final_response_count\""

  bigquery_config {
    table          = "${google_bigquery_table.rcs_timeseris.project}.${google_bigquery_table.rcs_timeseris.dataset_id}.${google_bigquery_table.rcs_timeseris.final_response_count_table_id}"
    write_metadata = true
  }

  depends_on = [
    google_project_iam_member.pubsub_bqEditor,
    google_project_iam_member.pubsub_bqMetadata
  ]
}

# ######################################################################

# Forward Order Event to BQ via Pub/Sub
resource "google_pubsub_subscription" "order_to_bq_sub" {
  name   = "order-event-to-bigquery"
  topic  = google_pubsub_topic.ingest_api.name
  labels = local.resource_labels
  filter = "attributes.entity=\"order-event\""

  bigquery_config {
    table          = "${google_bigquery_table.raw_order_events.project}.${google_bigquery_table.raw_order_events.dataset_id}.${google_bigquery_table.raw_order_events.table_id}"
    write_metadata = true
  }

  depends_on = [
    google_project_iam_member.pubsub_bqEditor,
    google_project_iam_member.pubsub_bqMetadata
  ]
}

# Forward Unknown Event to BQ via Pub/Sub
resource "google_pubsub_subscription" "unknown_to_bq_sub" {
  name   = "unknown-to-bigquery"
  topic  = google_pubsub_topic.ingest_api.name
  labels = local.resource_labels
  filter = "attributes.entity=\"unknown\""

  bigquery_config {
    table          = "${google_bigquery_table.raw_unknown.project}.${google_bigquery_table.raw_unknown.dataset_id}.${google_bigquery_table.raw_unknown.table_id}"
    write_metadata = true
  }

  depends_on = [
    google_project_iam_member.pubsub_bqEditor,
    google_project_iam_member.pubsub_bqMetadata
  ]
}

# ######################################################################

# Forward Order Event to Message Handler
resource "google_pubsub_subscription" "order_to_message_handler" {
  name   = "order-event-to-message-handler"
  topic  = google_pubsub_topic.ingest_api.name
  labels = local.resource_labels
  filter = "attributes.entity=\"order-event\""

  push_config {
    push_endpoint = google_cloud_run_v2_service.message_handler.uri
    oidc_token {
      # service_account_name = google_service_account.ingest_api.email
      service_account_email = google_service_account.ingest_api.email
    }
  }

  # Message retention duration (e.g., 1 hour)
  message_retention_duration = "3600s"
  # Acknowledge deadline (e.g., 30 seconds)
  ack_deadline_seconds = 30

  depends_on = [
    google_project_iam_member.token_creator,
    google_project_iam_member.cloudrun_invoker,
    google_project_iam_member.cloud_monitoring_writer
  ]
}

# ######################################################################

# Forward RCS Time Series Metrics (Request Count) to Message Handler
resource "google_pubsub_subscription" "rcs_timeseris_to_message_handler" {
  name   = "rcs-timeserics-to-message-handler"
  topic  = google_pubsub_topic.ingest_api.name
  labels = local.resource_labels
  filter = "attributes.entity=\"custom.googleapis.com/rcs/sip/request_count\" OR attributes.entity=\"custom.googleapis.com/rcs/sip/final_response_count\""

  push_config {
    push_endpoint = google_cloud_run_v2_service.rcs_metrics_message_handler.uri
    oidc_token {
      service_account_email = google_service_account.ingest_api.email
    }
  }

  # Message retention duration (e.g., 1 hour)
  message_retention_duration = "3600s"
  # Acknowledge deadline (e.g., 30 seconds)
  ack_deadline_seconds = 30

  depends_on = [
    google_project_iam_member.token_creator,
    google_project_iam_member.cloudrun_invoker,
    google_project_iam_member.cloud_monitoring_writer
  ]
}