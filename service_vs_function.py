import time
import requests
import os
from google.cloud.run_v2 import JobsClient, ExecutionsClient
from typing import List

# --- Configuration ---
GCP_PROJECT_ID = "dulcet-equinox-444420-d8"
GCP_REGION = "us-west1"
CLOUD_SERVICE_URL = "https://cloud-service-418100612281.us-west1.run.app"
CLOUD_JOB_NAME = "cloud-job"

# --- New Configuration: Number of test runs ---
NUM_RUNS = 10

# Get the OAuth2 token for invoking the service
# This assumes you are authenticated via 'gcloud auth login'
# and 'gcloud auth application-default login'
try:
    token = os.popen('gcloud auth print-identity-token').read().strip()
    if not token:
        raise ValueError("Token is empty. Ensure 'gcloud auth print-identity-token' is working.")
    headers = {"Authorization": f"Bearer {token}"}
except Exception as e:
    print(f"🔴 FATAL: Could not get gcloud identity token. Error: {e}")
    print("Please ensure you are authenticated with 'gcloud auth login' and 'gcloud auth application-default login'.")
    exit(1)


def measure_service_total_time(url: str) -> float:
    """Measures the total round-trip time for a single request to a Cloud Run service."""
    print(f"  Testing Cloud Run Service at: {url}")
    start_time = time.perf_counter()
    try:
        response = requests.get(url, headers=headers, timeout=300)
        response.raise_for_status()  # Raise an exception for bad status codes
        end_time = time.perf_counter()
        duration = end_time - start_time
        print(f"  Service returned a response in {duration:.4f} seconds.")
        return duration
    except requests.exceptions.RequestException as e:
        print(f"  Error calling service: {e}")
        return -1.0


def measure_job_total_time(project_id: str, region: str, job_name: str) -> float:
    """Triggers a Cloud Run Job and measures its total execution time."""
    print(f"  Testing Cloud Run Job: {job_name}")
    job_client = JobsClient()
    execution_client = ExecutionsClient()

    parent = f"projects/{project_id}/locations/{region}/jobs/{job_name}"

    try:
        # Start the job execution and wait for it to be created
        operation = job_client.run_job(name=parent)
        print("  Waiting for job execution to be created...")
        execution = operation.result(timeout=180)  # 3-minute timeout
        creation_time = execution.create_time
        print(f"  Job execution '{execution.name.split('/')[-1]}' created. Polling for completion...")

        # Poll until the job execution is finished
        while not execution.completion_time:
            time.sleep(5)  # Wait 5 seconds between checks
            execution = execution_client.get_execution(name=execution.name)

        completion_time = execution.completion_time
        duration = (completion_time - creation_time).total_seconds()

        if execution.failed_count > 0:
            print(f"  Job execution completed with failures in {duration:.4f} seconds.")
        else:
            print(f"  Job execution succeeded in {duration:.4f} seconds.")

        return duration

    except Exception as e:
        print(f"  An error occurred: {e}")
        return -1.0


def print_statistics(label: str, times: List[float]):
    """Prints descriptive statistics for a list of run times."""
    print("\n" + "=" * 40)
    print(f"📊 Statistics for: {label}")
    print("=" * 40)

    if not times:
        print("No successful runs to analyze.")
        return

    print(f"Total successful runs: {len(times)}")
    if times:
        print(f"Fastest run: {min(times):.4f} seconds")
        print(f"Slowest run: {max(times):.4f} seconds")
        print(f"Average run: {(sum(times) / len(times)):.4f} seconds")


if __name__ == "__main__":
    print(f"--- 🚀 Starting Total Execution Time Test ({NUM_RUNS} runs each) ---")

    service_times: List[float] = []
    job_times: List[float] = []

    # --- 1. Test Cloud Run Service ---
    print(f"\n--- Testing Cloud Run Service {NUM_RUNS} times ---")
    for i in range(1, NUM_RUNS + 1):
        print(f"\n[Service Run #{i:02d}/{NUM_RUNS}]")
        service_time = measure_service_total_time(CLOUD_SERVICE_URL)
        if service_time > 0:
            service_times.append(service_time)
        time.sleep(1)  # Small delay between requests

    # --- 2. Test Cloud Run Job ---
    print(f"\n--- Testing Cloud Run Job {NUM_RUNS} times ---")
    for i in range(1, NUM_RUNS + 1):
        print(f"\n[Job Run #{i:02d}/{NUM_RUNS}]")
        job_time = measure_job_total_time(GCP_PROJECT_ID, GCP_REGION, CLOUD_JOB_NAME)
        if job_time > 0:
            job_times.append(job_time)
        time.sleep(5)  # Delay between job runs to avoid potential rate limits

    # --- 3. Final Summary ---
    print("\n\n--- ✅ Test Complete: Final Summary ---")
    print_statistics("Cloud Run Service (Request/Response Latency)", service_times)
    print_statistics("Cloud Run Job (Execution Lifecycle)", job_times)