resource "google_pubsub_topic" "rcs_topic" {
  name   = "rcs_topic"
  labels = local.resource_labels
}

# Forward All RCS Metrics (Raw Data) to BQ via Pub/Sub
resource "google_pubsub_subscription" "rcs_metrics_to_bq_sub" {
  name   = "rcs-metrics-to-bigquery"
  topic  = google_pubsub_topic.rcs_topic.name
  labels = local.resource_labels
  
  bigquery_config {
    table          = "${google_bigquery_table.raw_rcs_metrics.project}.${google_bigquery_table.raw_rcs_metrics.dataset_id}.${google_bigquery_table.raw_rcs_metrics.table_id}"
    write_metadata = true
  }

  depends_on = [
    google_project_iam_member.pubsub_bqEditor,
    google_project_iam_member.pubsub_bqMetadata
  ]
}