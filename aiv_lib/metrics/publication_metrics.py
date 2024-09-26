from google.cloud import monitoring_v3
from google.api import metric_pb2 as ga_metric
from google.api import label_pb2 as ga_label

project_id = "socialmediabot-398507"
client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{project_id}"
service_name = "publisher_service"

# Metric 1: publication_started
descriptor_started = ga_metric.MetricDescriptor()
descriptor_started.type = f"custom.googleapis.com/{service_name}/cycle_started"
descriptor_started.metric_kind = ga_metric.MetricDescriptor.MetricKind.GAUGE # Changed to CUMULATIVE
descriptor_started.value_type = ga_metric.MetricDescriptor.ValueType.INT64
descriptor_started.description = "Counts each time a publication cycle starts."

# Metric 2: publication_result (with label)
descriptor_result= ga_metric.MetricDescriptor()
descriptor_result.type = f"custom.googleapis.com/{service_name}/cycle_result"
descriptor_result.metric_kind = ga_metric.MetricDescriptor.MetricKind.CUMULATIVE  # Changed to CUMULATIVE
descriptor_result.value_type = ga_metric.MetricDescriptor.ValueType.INT64
descriptor_result.description = "Logs whether the publication cycle was a success or error."
result_label = ga_label.LabelDescriptor()
result_label.key = "result"
result_label.value_type = ga_label.LabelDescriptor.ValueType.STRING
result_label.description = "Result of the publication cycle: success or error."
descriptor_result.labels.append(result_label)

# Metric 3: publication_duration
descriptor_duration = ga_metric.MetricDescriptor()
descriptor_duration.type = f"custom.googleapis.com/{service_name}/cycle_duration"
descriptor_duration.metric_kind = ga_metric.MetricDescriptor.MetricKind.GAUGE  # GAUGE is fine here
descriptor_duration.value_type = ga_metric.MetricDescriptor.ValueType.DOUBLE
descriptor_duration.description = "Logs the total time taken for a publication cycle."

# Create the metric descriptors
client.create_metric_descriptor(name=project_name, metric_descriptor=descriptor_started)
client.create_metric_descriptor(name=project_name, metric_descriptor=descriptor_result)
client.create_metric_descriptor(name=project_name, metric_descriptor=descriptor_duration)

print("Custom metrics for publication_service created successfully.")
