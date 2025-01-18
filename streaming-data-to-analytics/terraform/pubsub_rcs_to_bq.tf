# Forward RCS Time Series Metrics (Request Count) to BQ via Pub/Sub
resource "google_pubsub_subscription" "rcs_metrics_to_bq_sub" {
  name   = "rcs-metrics-to-bigquery"
  topic  = google_pubsub_topic.ingest_api.name
  labels = local.resource_labels
  filter = "attributes.metric_type=\"custom.googleapis.com/rcs/sip/request_count\" OR attributes.metric_type=\"custom.googleapis.com/rcs/sip/final_response_count\""

  bigquery_config {
    table          = "${google_bigquery_table.raw_rcs_metrics.project}.${google_bigquery_table.raw_rcs_metrics.dataset_id}.${google_bigquery_table.raw_rcs_metrics.table_id}"
    write_metadata = true
  }

  depends_on = [
    google_project_iam_member.pubsub_bqEditor,
    google_project_iam_member.pubsub_bqMetadata
  ]
}