resource "google_pubsub_topic" "order_topic" {
  name   = "order_topic"
  labels = local.resource_labels
}

# ######################################################################

# Forward Order Event to BQ via Pub/Sub
resource "google_pubsub_subscription" "raw_order_to_bq" {
  name   = "order-event-to-bigquery"
  topic  = google_pubsub_topic.order_topic.name
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
resource "google_pubsub_subscription" "raw_unknown_to_bq" {
  name   = "unknown-event-to-bigquery"
  topic  = google_pubsub_topic.order_topic.name
  labels = local.resource_labels
  filter = "attributes.entity=\"unknown-event\""

  bigquery_config {
    table          = "${google_bigquery_table.raw_unknown_events.project}.${google_bigquery_table.raw_unknown_events.dataset_id}.${google_bigquery_table.raw_unknown_events.table_id}"
    write_metadata = true
  }

  depends_on = [
    google_project_iam_member.pubsub_bqEditor,
    google_project_iam_member.pubsub_bqMetadata
  ]
}

# ######################################################################

# Forward Order Event to Order Handler
resource "google_pubsub_subscription" "order_event_to_order_handler" {
  name   = "order-event-to-order-handler"
  topic  = google_pubsub_topic.order_topic.name
  labels = local.resource_labels
  filter = "attributes.entity=\"order-event\""

  push_config {
    push_endpoint = google_cloud_run_v2_service.order_handler.uri
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

