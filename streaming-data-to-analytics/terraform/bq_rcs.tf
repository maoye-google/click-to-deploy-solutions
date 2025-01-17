resource "google_bigquery_dataset" "rcs_metrics" {
  dataset_id  = "rcs_metrics"
  description = "Store RCS Metrics data ingested through Pub/sub"
  location    = var.region
  labels      = local.resource_labels
}

# ######################################################################

resource "google_bigquery_table" "rcs_timeseris_request_count" {
  dataset_id          = google_bigquery_dataset.rcs_metrics.dataset_id
  table_id            = "request_count"
  description         = "Store Request Count Events streamed received by the Ingest API"
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

resource "google_bigquery_table" "rcs_timeseris_final_response_count" {
  dataset_id          = google_bigquery_dataset.rcs_metrics.dataset_id
  table_id            = "final_response_count"
  description         = "Store Final Response Count Events streamed received by the Ingest API"
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
