resource "google_logging_metric" "order_count2" {
  project = var.project_id
  name   = "order_count_2"
  filter = "severity>=DEFAULT AND resource.type = \"cloud_run_revision\" AND resource.labels.service_name = \"message-handler\" AND textPayload=~\"INFO\\:root\\:Received\\sOrder.*\""

  description = "Count of Order Received Notification from Log"

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }
}

resource "google_monitoring_notification_channel" "email_channel" {
  project = var.project_id
  type   = "email"
  display_name = "Alert Sent via Email"
  labels = {
    email_address = "maoye@google.com" # Replace with your email
  }
}

resource "google_monitoring_alert_policy" "rate_exceed_policy" {
  project = var.project_id
  display_name = "If request rate exceeds 100/m"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Rate Above Threshold"
    condition_threshold {
      filter     = "resource.type = \"cloud_run_revision\" AND metric.type = \"logging.googleapis.com/user/order_count_2\""
      duration   = "0s"
      comparison = "COMPARISON_GT"
      threshold_value = 100
      trigger {
        count = 1
      }
      aggregations {
        alignment_period   = "60s" # 1 minute
        cross_series_reducer = "REDUCE_SUM"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.email_channel.name
  ]

  # Optional: Documentation to be included with notifications
  documentation {
    content   = "The received order count has exceeded the threshold. Investigate the logs for details."
    mime_type = "text/markdown"
  }

  depends_on=[
    google_logging_metric.order_count2,
    google_monitoring_notification_channel.email_channel
  ]

}