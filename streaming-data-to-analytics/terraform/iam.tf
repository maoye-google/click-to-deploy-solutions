resource "google_service_account" "ingest_api" {
  account_id   = local.ingest_api_name
  display_name = "Cloud Function Ingest API"
  create_ignore_already_exists = true
}

# Grant the Permission to modify pubsub subscriptions, and consumer messages
resource "google_project_iam_member" "pubsub_editor" {
  project = var.project_id
  role    = "roles/pubsub.editor"
  member  = "serviceAccount:${google_service_account.ingest_api.email}"
}

resource "google_project_iam_member" "token_creator" {
  project = var.project_id
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:${google_service_account.ingest_api.email}"
}

resource "google_project_iam_member" "cloudrun_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.ingest_api.email}"
}

resource "google_project_iam_member" "cloudfunction_invoker" {
  project = var.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "serviceAccount:${google_service_account.ingest_api.email}"
}


# Grant the permissions to write to Cloud Monitoring
resource "google_project_iam_member" "cloud_monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.editor"
  member  = "serviceAccount:${google_service_account.ingest_api.email}"
}

# Grant the permissions to write to BigQuery
resource "google_project_iam_member" "pubsub_bqEditor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  # member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
  member  = "serviceAccount:${google_service_account.ingest_api.email}"
}

# Grant the Permission to get Bigquery metadata
resource "google_project_iam_member" "pubsub_bqMetadata" {
  project = var.project_id
  role    = "roles/bigquery.metadataViewer"
  # member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
  member  = "serviceAccount:${google_service_account.ingest_api.email}"
}

# Grant the permissions to write to BigQuery
resource "google_project_iam_member" "pubsub_bqEditor_2" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
  # member  = "serviceAccount:${google_service_account.ingest_api.email}"
}

# Grant the Permission to get Bigquery metadata
resource "google_project_iam_member" "pubsub_bqMetadata_2" {
  project = var.project_id
  role    = "roles/bigquery.metadataViewer"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
  # member  = "serviceAccount:${google_service_account.ingest_api.email}"
}

