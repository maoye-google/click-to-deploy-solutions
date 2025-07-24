resource "google_bigquery_dataset" "rcs_metrics" {
  dataset_id  = "rcs_metrics"
  description = "Store RCS Metrics data ingested through Pub/sub"
  location    = var.region
  labels      = local.resource_labels
}

# ######################################################################

resource "google_bigquery_table" "raw_rcs_metrics" {
  dataset_id          = google_bigquery_dataset.rcs_metrics.dataset_id
  table_id            = "raw_rcs_metrics"
  description         = "Store Raw RCS Metrics Event (from Pub/Sub) received by the Ingest API"
  deletion_protection = false
  labels              = local.resource_labels

  time_partitioning {
    type  = "DAY"
    field = "publish_time"
  }

  schema = <<EOF
  [
    {
      "name": "subscription_name",
      "type": "STRING",
      "mode": "NULLABLE"
    },
    {
      "name": "message_id",
      "type": "STRING",
      "mode": "NULLABLE"
    },
    {
      "name": "publish_time",
      "type": "TIMESTAMP",
      "mode": "NULLABLE"
    },
    {
      "name": "attributes",
      "type": "STRING",
      "mode": "NULLABLE"
    },
    {
      "name": "data",
      "type": "STRING",
      "mode": "NULLABLE"
    }
  ]
  EOF
}

# ######################################################################

resource "google_bigquery_table" "rcs_metrics_all" {
  dataset_id          = google_bigquery_dataset.rcs_metrics.dataset_id
  table_id            = "rcs_metrics_all"
  description         = "Store All Received RCS Metrics"
  deletion_protection = false
  labels              = local.resource_labels

  time_partitioning {
    type  = "DAY"
    field = "start_time"
  }

  schema = <<EOF
  [
    {
      "name": "metric_type",
      "type": "STRING",
      "mode": "NULLABLE"
    },
    {
      "name": "conversation_type",
      "type": "STRING",
      "mode": "NULLABLE"
    },
    {
      "name": "carrier",
      "type": "STRING",
      "mode": "NULLABLE"
    },
    {
      "name": "sip_method",
      "type": "STRING",
      "mode": "NULLABLE"
    },
    {
      "name": "response_code",
      "type": "STRING",
      "mode": "NULLABLE"
    },
    {
      "name": "direction",
      "type": "STRING",
      "mode": "NULLABLE"
    },
    {
      "name": "start_time",
      "type": "TIMESTAMP",
      "mode": "NULLABLE"
    },
    {
      "name": "end_time",
      "type": "TIMESTAMP",
      "mode": "NULLABLE"
    },
    {
      "name": "value",
      "type": "INTEGER",
      "mode": "NULLABLE"
    },
    {
      "name": "client_vendor",
      "type": "STRING",
      "mode": "NULLABLE"
    }
  ]
  EOF

}