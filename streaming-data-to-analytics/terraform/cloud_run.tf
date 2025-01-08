# Ingest_API Cloud Run service
resource "google_cloud_run_v2_service" "ingest_api" {
  name     = local.function_name
  location = var.region

  template {
    service_account = google_service_account.ingest_api.email
    containers {
      image = local.ingest_api_container
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "TOPIC_ID"
        value = google_pubsub_topic.ingest_api.name
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



# Message Handler Cloud Run service
resource "google_cloud_run_v2_service" "message_handler" {
  name     = local.handler_name
  location = var.region

  template {
    service_account = google_service_account.ingest_api.email
    containers {
      image = local.message_handler_container
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