import os
import time
import requests
from google.cloud.run_v2 import JobsClient
from google.cloud import logging

# --- Configuration ---
GCP_PROJECT_ID = "dulcet-equinox-444420-d8"
GCP_REGION = "us-west1"
CLOUD_SERVICE_URL = "https://cloud-service-418100612281.us-west1.run.app"
CLOUD_JOB_NAME = "cloud-job"

# Get the OAuth2 token for invoking the service
token = os.popen('gcloud auth print-identity-token').read().strip()
headers = {"Authorization": f"Bearer {token}"}


def test_service_cold_start(url: str) -> float:
    """Measures the response time of a Cloud Run service endpoint."""
    print(f"Testing Cloud Run Service at: {url}")
    start_time = time.perf_counter()
    try:
        response = requests.get(url, headers=headers, timeout=300)
        response.raise_for_status()
        end_time = time.perf_counter()
        duration = end_time - start_time
        print(f"Service responded in {duration:.4f} seconds.")
        return duration
    except requests.exceptions.RequestException as e:
        print(f"Error calling service: {e}")
        return -1.0

def test_job_cold_start(project_id: str, region: str, job_name: str) -> float:
    """Triggers a Cloud Run Job and measures its startup time via logs."""
    print(f"Testing Cloud Run Job: {job_name}")
    job_client = JobsClient()
    logging_client = logging.Client(project=project_id) # <-- CORRECTED INITIALIZATION

    parent = f"projects/{project_id}/locations/{region}/jobs/{job_name}"

    try:
        # 1. Start the job execution
        operation = job_client.run_job(name=parent)
        execution = operation.result()
        execution_id = execution.name.split("/")[-1]
        creation_time = execution.create_time

        print(f"Job execution '{execution_id}' created at {creation_time.isoformat()}.")
        print("Searching for startup log...")

        # 2. Poll logs for the startup message
        start_poll_time = time.time()
        log_filter = f"""
            resource.type="cloud_run_job"
            resource.labels.job_name="{job_name}"
            textPayload="JOB_CONTAINER_STARTED_LOG:{execution_id}"
        """

        while time.time() - start_poll_time < 300: # 5-minute timeout
            # The client's list_entries method is used to query logs
            for entry in logging_client.list_entries(filter_=log_filter):
                log_timestamp = entry.timestamp
                duration = (log_timestamp - creation_time).total_seconds()
                print(f"Startup log found at {log_timestamp.isoformat()}.")
                print(f"Job cold start was {duration:.4f} seconds.")
                return duration
            time.sleep(2) # Wait before polling again

        print("Error: Timed out waiting for job startup log.")
        return -1.0

    except Exception as e:
        print(f"An error occurred: {e}")
        return -1.0

if __name__ == "__main__":
    print("--- 🚀 Starting Apples-to-Apples Cold Start Test ---")

    # Ensure the service is scaled to zero by not sending traffic for ~15 mins
    service_time = test_service_cold_start(CLOUD_SERVICE_URL)

    print("\n" + "-"*40 + "\n")

    job_time = test_job_cold_start(GCP_PROJECT_ID, GCP_REGION, CLOUD_JOB_NAME)

    print("\n--- ✅ Test Complete ---")
    if service_time > 0:
        print(f"Service Cold Start Time: {service_time:.4f} seconds")
    if job_time > 0:
        print(f"Job Cold Start Time:     {job_time:.4f} seconds")