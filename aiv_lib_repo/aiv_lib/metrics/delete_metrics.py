from google.cloud import monitoring_v3

def delete_custom_metric(project_id, metric_type):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"
    metric_descriptor_name = f"{project_name}/metricDescriptors/{metric_type}"

    try:
        client.delete_metric_descriptor(name=metric_descriptor_name)
        print(f"Metric '{metric_type}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting metric '{metric_type}': {e}")

if __name__ == "__main__":
    project_id = "socialmediabot-398507"
    project_name = f"projects/{project_id}"
    service_name = "publisher_service"
    metric_type = f"custom.googleapis.com/{service_name}/cycle_started"
    delete_custom_metric(project_id, metric_type)

