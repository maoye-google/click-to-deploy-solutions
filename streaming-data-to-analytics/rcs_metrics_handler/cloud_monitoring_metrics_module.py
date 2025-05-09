from google.api import metric_pb2 as ga_metric
from google.api import label_pb2 as ga_label
import time
import os
import json
import base64
import logging
from flask import Flask, request
from datetime import datetime
from google.cloud import pubsub_v1, monitoring_v3
from google.cloud.monitoring_v3.types import TimeSeries, TypedValue, Point, TimeInterval
from google.protobuf.json_format import MessageToDict, MessageToJson
from google.protobuf.timestamp_pb2 import Timestamp
import google.protobuf.json_format

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class GoogleCloudMonitoringUtil:
    """
    Utility class for interacting with Google Cloud Monitoring to manage
    and write data to custom metrics.
    """

    def metric_descriptor_exists(self):
        """
        Checks if a metric descriptor exists.

        Args:
            metric_type: The full metric type identifier (e.g., "custom.googleapis.com/my_metric").

        Returns:
            True if the metric descriptor exists, False otherwise.
        """
        if (self.metric_already_exist):
            return True
        
        metric_name = f"{self.project_name}/metricDescriptors/{self.metric_type}"

        try:
        
            self.client.get_metric_descriptor(name=metric_name)
            logger.debug(f"Metric descriptor {metric_name} already exists.")
            self.metric_already_exist = True
            return True
        
        except Exception as e:
            if ("does not exist" in str(e)) or ("Could not find" in str(e)):
                logger.debug(f"Metric descriptor {metric_name} does not exist.")
                return False
            else:
                logger.error(f"Error checking metric descriptor: {e}")
                raise e
            

    def create_metric_descriptor(
        self,
        metric_kind=ga_metric.MetricDescriptor.MetricKind.CUMULATIVE,
        value_type=ga_metric.MetricDescriptor.ValueType.INT64,
        description="Custom metric"
    ):
        """
        Creates a custom metric descriptor if it doesn't exist.

        Args:
            metric_kind: The kind of metric (e.g., GAUGE, CUMULATIVE, DELTA).
            value_type: The data type of the metric (e.g., INT64, DOUBLE, BOOL, STRING, DISTRIBUTION).
            description: A description of the metric.
            labels: A list of label descriptors (list of google.api.label_pb2.LabelDescriptor).

        Returns:
            The created metric descriptor (google.api.metric_pb2.MetricDescriptor) or None if it already exists.
        """
        if self.metric_descriptor_exists():
            logger.debug(f"Descriptor for {self.metric_type} already exist")
            return None

        logger.debug(f"Ready to create User Metric Descriptor for {self.metric_type}")

        descriptor = ga_metric.MetricDescriptor()
        descriptor.type = self.metric_type
        descriptor.metric_kind = metric_kind
        descriptor.value_type = value_type
        descriptor.description = description

        if self.labels:
            label_descriptors = []
            for key in self.labels:
                label_desc = ga_label.LabelDescriptor(
                    key=key,
                    value_type=ga_label.LabelDescriptor.ValueType.STRING
                )
                label_descriptors.append(label_desc)
            descriptor.labels.extend(label_descriptors)

        try:
            descriptor = self.client.create_metric_descriptor(
                name=self.project_name, metric_descriptor=descriptor
            )
            logger.info(f"Created User Metric Descriptor for {self.metric_type}")
            return descriptor
        except Exception as e:
            logger.debug(f"Metric descriptor for {self.metric_type} cannot be created !")
            raise e


    def __init__(self, project_id, metric_type,labels=None):
        """
        Initializes the GoogleCloudMonitoringUtil with your project ID.

        Args:
            project_id: Your Google Cloud project ID.
        """
        self.project_id = project_id
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"
        self.metric_already_exist = False
        self.metric_type = metric_type
        # self.metric_type = f"custom.googleapis.com/{metric_type}"
        self.labels = labels
        self.metric_descriptor = self.create_metric_descriptor()

    
    def write_time_series_data(self, start_time, end_time, value, metric_labels=None):
        if not self.metric_already_exist:
            logger.warning(f"Metric descriptor {self.metric_type} does not exist. Cannot write time series data.")
            return

        point = monitoring_v3.Point()
        point.value.int64_value = int(value)
        
        _date_format = "%Y-%m-%dT%H:%M:%Sz"
        point.interval.start_time = datetime.strptime(start_time, _date_format)
        point.interval.end_time = datetime.strptime(end_time, _date_format)

        single_time_series = monitoring_v3.TimeSeries({
            "metric":{"type":self.metric_type,"labels":{}},
            "resource":{"type":"global","labels":{}},
            "points":[point]
        })

        if metric_labels:
            for key, label_value in metric_labels.items():
                single_time_series.metric.labels[key] = label_value

        logger.debug(f"Ready to write 1 unit time series data.")
        request = monitoring_v3.CreateTimeSeriesRequest(
            name=self.project_name,
            time_series=[single_time_series]
        )
        self.client.create_time_series(request=request)
        logger.debug(f"Successfully wrote 1 unit time series data.")


# # Example Usage:
# if __name__ == "__main__":
#     PROJECT_ID = "your-gcp-project-id"  # Replace with your project ID
#     METRIC_TYPE = "custom.googleapis.com/my_custom_metric_util"

#     monitoring_util = GoogleCloudMonitoringUtil(PROJECT_ID)

#     # Create a metric descriptor (if it doesn't exist)
#     monitoring_util.create_metric_descriptor(
#         METRIC_TYPE, description="My custom metric"
#     )

#     # Write time series data
#     for _ in range(5):
#         labels = {"environment": "production", "location": "us-central1"}
#         monitoring_util.write_time_series_data(METRIC_TYPE, random.uniform(0.5, 100), labels)
#         time.sleep(60)

#     # (Optional) Delete the metric descriptor
#     # monitoring_util.delete_metric_descriptor(METRIC_TYPE)