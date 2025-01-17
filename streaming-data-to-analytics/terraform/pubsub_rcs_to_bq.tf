# Forward RCS Time Series Metrics (Request Count) to BQ via Pub/Sub
resource "google_pubsub_subscription" "rcs_timeseris_request_count_to_bq_sub" {
  name   = "rcs-timeseries-request-count-to-bigquery"
  topic  = google_pubsub_topic.ingest_api.name
  labels = local.resource_labels
  filter = "attributes.metric_type=\"custom.googleapis.com/rcs/sip/request_count\""

  bigquery_config {
    table          = "${google_bigquery_table.rcs_timeseris_request_count.project}.${google_bigquery_table.rcs_timeseris_request_count.dataset_id}.${google_bigquery_table.rcs_timeseris_request_count.table_id}"
    write_metadata = true
  }

  depends_on = [
    google_project_iam_member.pubsub_bqEditor,
    google_project_iam_member.pubsub_bqMetadata
  ]
}

# Forward RCS Time Series Metrics (Final Response Count) to BQ via Pub/Sub
resource "google_pubsub_subscription" "rcs_timeseris_final_response_count_to_bq_sub" {
  name   = "rcs-timeseries-finl-response-count-to-bigquery"
  topic  = google_pubsub_topic.ingest_api.name
  labels = local.resource_labels
  filter = "attributes.metric_type=\"custom.googleapis.com/rcs/sip/final_response_count\""

  bigquery_config {
    table          = "${google_bigquery_table.rcs_timeseris_final_response_count.project}.${google_bigquery_table.rcs_timeseris_final_response_count.dataset_id}.${google_bigquery_table.rcs_timeseris_final_response_count.table_id}"
    write_metadata = true
  }

  depends_on = [
    google_project_iam_member.pubsub_bqEditor,
    google_project_iam_member.pubsub_bqMetadata
  ]
}