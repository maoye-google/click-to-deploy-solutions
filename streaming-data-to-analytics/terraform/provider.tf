terraform {
  backend "gcs" {
  }

  required_providers {
    google = {
      version = "~> 5.21.0"
    }
  }

  provider_meta "google" {
    module_name = "cloud-solutions/streaming-data-to-analytics-v0.1"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
