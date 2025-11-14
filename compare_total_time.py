import time
import requests
import os
from google.cloud.run_v2 import JobsClient, ExecutionsClient

# --- Configuration ---
GCP_PROJECT_ID = "dulcet-equinox-444420-d8"
GCP_REGION = "us-west1"
CLOUD_SERVICE_URL = "https://cloud-service-418100612281.us-west1.run.app"
CLOUD_JOB_NAME = "cloud-job"

# Get the OAuth2 token for invoking the service
token = os.popen('gcloud auth print-identity-token').read().strip()
headers = {"Authorization": f"Bearer {token}"}


def measure_service_total_time(url: str) -> float:
    """Measures the total round-trip time for a request to a Cloud Run service."""
    print(f"Testing Cloud Run Service at: {url}")
    start_time = time.perf_counter()
    try:
        response = requests.get(url, headers=headers, timeout=300)
        response.raise_for_status()  # Raise an exception for bad status codes
        end_time = time.perf_counter()
        duration = end_time - start_time
        print(f"Service returned a response in {duration:.4f} seconds.")
        return duration
    except requests.exceptions.RequestException as e:
        print(f"Error calling service: {e}")
        return -1.0


def measure_job_total_time(project_id: str, region: str, job_name: str) -> float:
    """Triggers a Cloud Run Job and measures its total execution time."""
    print(f"Testing Cloud Run Job: {job_name}")
    job_client = JobsClient()
    execution_client = ExecutionsClient()

    parent = f"projects/{project_id}/locations/{region}/jobs/{job_name}"

    try:
        # Start the job execution and wait for it to be created
        operation = job_client.run_job(name=parent)
        print("Waiting for job execution to be created...")
        execution = operation.result(timeout=180)  # 3-minute timeout
        creation_time = execution.create_time
        print(f"Job execution '{execution.name.split('/')[-1]}' created. Polling for completion...")

        # Poll until the job execution is finished
        while not execution.completion_time:
            time.sleep(5)  # Wait 5 seconds between checks
            execution = execution_client.get_execution(name=execution.name)

        completion_time = execution.completion_time
        duration = (completion_time - creation_time).total_seconds()

        if execution.failed_count > 0:
            print(f"Job execution completed with failures in {duration:.4f} seconds.")
        else:
            print(f"Job execution succeeded in {duration:.4f} seconds.")

        return duration

    except Exception as e:
        print(f"An error occurred: {e}")
        return -1.0


if __name__ == "__main__":
    print("--- 🚀 Starting Total Execution Time Test ---")

    service_time = measure_service_total_time(CLOUD_SERVICE_URL)

    print("\n" + "-" * 40 + "\n")

    job_time = measure_job_total_time(GCP_PROJECT_ID, GCP_REGION, CLOUD_JOB_NAME)

    print("\n--- ✅ Test Complete ---")
    if service_time > 0:
        print(f"Service Total Time (Latency): {service_time:.4f} seconds")
    if job_time > 0:
        print(f"Job Total Time (Lifecycle):   {job_time:.4f} seconds")