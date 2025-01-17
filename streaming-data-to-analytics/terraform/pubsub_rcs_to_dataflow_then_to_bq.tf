# Forward RCS Time Series Metrics to DataFlow
resource "google_pubsub_subscription" "rcs_timeseris_to_dataflow" {
  name  = "rcs-timeseries-to-dataflow"
  topic = google_pubsub_topic.ingest_api.name
  filter = "attributes.metric_type=\"custom.googleapis.com/rcs/sip/request_count\" OR attributes.metric_type=\"custom.googleapis.com/rcs/sip/final_response_count\""

  # Ack deadline, retry policy, etc. can be added here

  # We DO NOT use bigquery_config here, as Dataflow will handle BigQuery writing
}


# ---------------------------------------------------------------

resource "google_project_service" "dataflow" {
  service = "dataflow.googleapis.com"
}

resource "google_storage_bucket" "dataflow_bucket" {
  name     = "rcs-metrics-bucket-dataflow"        # Replace with a unique name
  location = var.region                                 # Choose your desired location
  project  = var.project_id                       # Replace with your project ID
}

# Grant necessary permissions to the service account
resource "google_project_iam_member" "dataflow_worker" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.ingest_api.email.email}"
}

resource "google_project_iam_member" "storage_object_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.ingest_api.email}"
}

resource "google_project_iam_member" "pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.ingest_api.email}"
}

resource "google_project_iam_member" "bigquery_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.ingest_api.email}"
}

resource "google_dataflow_job" "pubsub_to_dataflow_to_bigquery" {
  provider                       = google
  name                           = "pubsub-to-dataflow-to-bigquery"
  region                         = var.region # Choose your region
  project                        = var.project_id
  temp_gcs_location              = "gs://${google_storage_bucket.dataflow_bucket.name}/temp"
  service_account_email          = google_service_account.ingest_api.email
  on_delete                      = "cancel"
  parameters = {
    inputSubscription = "projects/your-gcp-project/subscriptions/your-pubsub-subscription-to-dataflow" # Get from Pub/Sub subscription resource
    outputTable       = "your-gcp-project:your_bigquery_dataset.your_bigquery_table" # Your BQ table
  }

  template_gcs_path = "gs://your-bucket-with-pipeline-code/dataflow_pipeline.py" # Path to your pipeline code in GCS
  depends_on = [
    google_project_service.dataflow
  ]
}