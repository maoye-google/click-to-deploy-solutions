# Define the bucket to host Cloud Functions Source Code (zip)

resource "google_storage_bucket" "cloudfunctions_tmp_bucket" {
 name          = var.project_id + "-cloudfunctions-tmp-bucket"
 location      = var.region
 storage_class = "STANDARD"

 uniform_bucket_level_access = true
}

# Upload Cloud Functions Source Zip to Cloud
resource "google_storage_bucket_object" "archive" {
  name   = var.rcs_metrics_saver_cf_zip_name
  bucket = google_storage_bucket.cloudfunctions_tmp_bucket.name
  source = "./tmp/"+var.rcs_metrics_saver_cf_zip_name # Path to the zip file containing your Cloud Function code
}