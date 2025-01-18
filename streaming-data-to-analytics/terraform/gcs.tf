# Define the bucket to host Cloud Functions Source Code (zip)

resource "google_storage_bucket" "cloudfunctions_tmp_bucket" {
 name          = var.project_id + "-cloudfunctions-tmp-bucket"
 location      = var.region
 storage_class = "STANDARD"

 uniform_bucket_level_access = true
}