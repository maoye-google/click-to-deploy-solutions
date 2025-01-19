# Ingest_API Cloud Run service
resource "google_cloud_run_v2_service" "ingest_api" {
  name     = local.ingest_api_name
  location = var.region
  deletion_protection = false

  template {
    service_account = google_service_account.ingest_api.email
    containers {
      image = local.ingest_api_container
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "ORDER_TOPIC_ID"
        value = google_pubsub_topic.order_topic.name
      }
      env {
        name  = "RCS_TOPIC_ID"
        value = google_pubsub_topic.rcs_topic.name
      }
    }
    annotations = {
      "autoscaling.knative.dev/minScale" = "1"
      "autoscaling.knative.dev/maxScale" = "10"
    }
    labels = local.resource_labels
  }

  traffic {
    percent         = 100
    type = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# Order Handler Cloud Run service (for Sample Message)
resource "google_cloud_run_v2_service" "order_handler" {
  name     = local.order_handler_name
  location = var.region
  deletion_protection = false

  template {
    service_account = google_service_account.ingest_api.email
    containers {
      image = local.order_handler_container
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
    }
    annotations = {
      "autoscaling.knative.dev/minScale" = "1"
      "autoscaling.knative.dev/maxScale" = "2"
    }
    labels = local.resource_labels
  }

  traffic {
    percent         = 100
    type = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}