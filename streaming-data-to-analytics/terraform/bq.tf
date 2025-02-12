resource "google_bigquery_dataset" "ecommerce_raw" {
  dataset_id  = "ecommerce_raw"
  description = "Store raw data ingested through Pub/sub"
  location    = var.region
  labels      = local.resource_labels
}

resource "google_bigquery_table" "raw_order_events" {
  dataset_id          = google_bigquery_dataset.ecommerce_raw.dataset_id
  table_id            = "order_events"
  description         = "Store order events streamed received by the Ingest API"
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
    "name": "data",
    "type": "STRING",
    "mode": "NULLABLE"
  },
    {
    "name": "attributes",
    "type": "STRING",
    "mode": "NULLABLE"
  }
]
EOF

}


resource "google_bigquery_table" "raw_unknown_events" {
  dataset_id          = google_bigquery_dataset.ecommerce_raw.dataset_id
  table_id            = "unknown_events"
  description         = "Store unknown events received by the Ingest API"
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "publish_time"
  }

  labels = local.resource_labels

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
    "name": "data",
    "type": "STRING",
    "mode": "NULLABLE"
  },
    {
    "name": "attributes",
    "type": "STRING",
    "mode": "NULLABLE"
  }
]
EOF

}