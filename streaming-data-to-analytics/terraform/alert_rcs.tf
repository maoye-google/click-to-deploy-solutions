resource "google_logging_metric" "rcs_request_count" {
  project = var.project_id
  name   = "rcs_request_count"
  filter = "severity>=DEFAULT AND resource.type = \"cloud_run_revision\" AND resource.labels.service_name = \"${google_cloud_run_v2_service.rcs_metrics_handler.name}\" AND textPayload=~\"RCS Metrics Logging.*${local.res_request_count_metrics_type}.*\""
  # value_extractor = "REGEXP_EXTRACT(textPayload, \"\\\"value\\\":\\s\\\"([0-9.]+)\\\"\")"

  description = "Count of RCS Request from Log"
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }
}

resource "google_logging_metric" "rcs_response_200_count" {
  project = var.project_id
  name   = "rcs_response_200_count"
  filter = "severity>=DEFAULT AND resource.type = \"cloud_run_revision\" AND resource.labels.service_name = \"${google_cloud_run_v2_service.rcs_metrics_handler.name}\" AND textPayload=~\"RCS Metrics Logging.*${local.res_final_response_count_metrics_type}.*\" AND textPayload=~\".*(\\\"response_code\\\":\\s\\\"200\\\")\""
  # value_extractor = "REGEXP_EXTRACT(textPayload, \"\\\"value\\\":\\s\\\"([0-9.]+)\\\"\")"
  
  description = "Count of RCS Final Response (200) from Log"
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }
}


resource "google_logging_metric" "rcs_response_non_200_count" {
  project = var.project_id
  name   = "rcs_response_non_200_count"
  filter = "severity>=DEFAULT AND resource.type = \"cloud_run_revision\" AND resource.labels.service_name = \"${google_cloud_run_v2_service.rcs_metrics_handler.name}\" AND textPayload=~\"RCS Metrics Logging.*${local.res_final_response_count_metrics_type}.*\" AND -textPayload=~\".*(\\\"response_code\\\":\\s\\\"200\\\")\""
  # value_extractor = "REGEXP_EXTRACT(textPayload, \"\\\"value\\\":\\s\\\"([0-9.]+)\\\"\")"
  
  description = "Count of RCS Final Response (None 200) from Log"

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }
}

resource "google_monitoring_notification_channel" "rcs_email_channel" {
  project = var.project_id
  type   = "email"
  display_name = "RCS Alert Sent via Email"
  labels = {
    email_address = "maoye@google.com" # Replace with your email
  }
}

resource "google_monitoring_alert_policy" "non_200_rcs_rate_exceed_policy" {
  project = var.project_id
  display_name = "If RCS Failure Rate exceeds 30/m"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Rate Above Threshold"
    condition_threshold {
      filter     = "resource.type = \"cloud_run_revision\" AND metric.type = \"logging.googleapis.com/user/rcs_response_non_200_count\""
      duration   = "0s"
      comparison = "COMPARISON_GT"
      threshold_value = 30
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
    google_monitoring_notification_channel.rcs_email_channel.name
  ]

  # Optional: Documentation to be included with notifications
  documentation {
    content   = "The RCS Non-200 Response Rate has exceeded the threshold. Investigate the logs for details."
    mime_type = "text/markdown"
  }

  depends_on=[
    google_logging_metric.rcs_request_count,
    google_logging_metric.rcs_response_200_count,
    google_logging_metric.rcs_response_non_200_count,
    google_monitoring_notification_channel.rcs_email_channel
  ]

}

# Dashboard
resource "google_monitoring_dashboard" "rcs_metrics_dashboard" {
  project = var.project_id
  dashboard_json = file(var.rcs_dashboard_json_path)
}