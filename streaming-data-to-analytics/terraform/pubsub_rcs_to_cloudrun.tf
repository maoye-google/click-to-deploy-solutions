# ######################################################################

# Forward RCS Time Series Metrics (Request Count) to Message Handler
resource "google_pubsub_subscription" "rcs_timeseris_to_rcs_metrics_handler" {
  name   = "rcs-timeserics-to-rcs-metrics-handler"
  topic  = google_pubsub_topic.ingest_api.name
  labels = local.resource_labels
  filter = "attributes.metric_type=\"custom.googleapis.com/rcs/sip/request_count\" OR attributes.metric_type=\"custom.googleapis.com/rcs/sip/final_response_count\""

  push_config {
    push_endpoint = google_cloud_run_v2_service.rcs_metrics_handler.uri
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