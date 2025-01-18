locals {
  resource_labels = merge(var.resource_labels, {
    deployed_by = "cloudbuild"
    repo        = "click-to-deploy-solutions"
    solution    = "streaming-data-to-analytics"
    terraform   = "true"
    }
  )

  function_name        = "ingest-api"
  ingest_api_container = "us-central1-docker.pkg.dev/${var.project_id}/docker-repo/gcp-ingest-api:${var.ingest_api_tag}"
  message_handler_container = "us-central1-docker.pkg.dev/${var.project_id}/docker-repo/gcp-message-handler:${var.message_handler_tag}"
  rcs_metrics_handler_container = "us-central1-docker.pkg.dev/${var.project_id}/docker-repo/gcp-rcs-metrics-handler:${var.rcs_metrics_handler_tag}"
  handler_name         = "message-handler"
  rcs_metrics_handler_name         = "rcs-metrics-handler"
}

variable "project_id" {
  description = "GCP Project ID"
  default     = null
}

variable "region" {
  type        = string
  description = "GCP region"
}

variable "ingest_api_tag" {
  description = "Ingest API container tag"
  default     = "latest"
}

variable "message_handler_tag" {
  description = "Message Handler container tag"
  default     = "latest"
}

variable "rcs_metrics_handler_tag" {
  description = "Android RCS Metrics Handler container tag"
  default     = "latest"
}

variable "resource_labels" {
  type        = map(string)
  description = "Resource labels"
  default     = {}
}

variable "rcs_resource_labels" {
  type        = map(string)
  description = "Android RCS Metrics"
  default     = {}
}

variable "dashboard_json_path" {
  description = "Native Dashboard for Received Order (Log Metrics)"
  type        = string
  default     = "../dashboard/order_count_dashboard.json"
}

variable "rcs_dashboard_json_path" {
  description = "Native Dashboard for RCS Metrics (Log Metrics)"
  type        = string
  default     = "../dashboard/rcs_metrics_dashboard.json"
}
