import time
import os
from google.cloud.run_v2 import JobsClient, ExecutionsClient
from typing import List, Dict

# --- Configuration ---
GCP_PROJECT_ID = "dulcet-equinox-444420-d8"
CLOUD_JOB_NAME = "cloud-job"
NUM_RUNS = 10

# A list of all regions where the job is deployed
JOB_REGIONS = ["us-west1", "us-west2", "us-south1"]


def measure_job_total_time(project_id: str, region: str, job_name: str) -> float:
    """Triggers a Cloud Run Job in a specific region and measures its total execution time."""
    print(f"  Testing Cloud Run Job: {job_name} in {region}")

    # Initialize clients. This uses Application Default Credentials (ADC).
    # Ensure you are authenticated via 'gcloud auth application-default login'.
    job_client = JobsClient()
    execution_client = ExecutionsClient()

    # The parent path now dynamically includes the region
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
        print("  No successful runs to analyze.")
        return

    print(f"  Total successful runs: {len(times)}")
    if times:
        print(f"  Fastest run: {min(times):.4f} seconds")
        print(f"  Slowest run: {max(times):.4f} seconds")
        print(f"  Average run: {(sum(times) / len(times)):.4f} seconds")


if __name__ == "__main__":
    print(f"--- 🚀 Starting Cloud Run Job Test ---")
    print(f"Job: {CLOUD_JOB_NAME}")
    print(f"Regions: {', '.join(JOB_REGIONS)}")
    print(f"Runs per region: {NUM_RUNS}")

    # Initialize the dictionary to store results per region
    job_times_by_region: Dict[str, List[float]] = {region: [] for region in JOB_REGIONS}

    # --- Test Cloud Run Jobs (Multi-Region) ---
    print(f"\n--- Testing Cloud Run Jobs in {len(JOB_REGIONS)} regions ({NUM_RUNS} times each) ---")

    # Loop over each region
    for region in JOB_REGIONS:
        print(f"\n" + "-" * 40)
        print(f"--- 🌎 Starting Job Tests for Region: {region} ---")
        print("-" * 40)

        # In each region, run the job NUM_RUNS times
        for i in range(1, NUM_RUNS + 1):
            print(f"\n[Job Run #{i:02d}/{NUM_RUNS} in {region}]")
            job_time = measure_job_total_time(GCP_PROJECT_ID, region, CLOUD_JOB_NAME)
            if job_time > 0:
                job_times_by_region[region].append(job_time)

            # Delay between job runs to avoid potential rate limits
            time.sleep(5)

            # --- Final Summary ---
    print("\n\n--- ✅ Test Complete: Final Summary ---")

    # Print stats for each job region
    for region, times in job_times_by_region.items():
        print_statistics(f"Cloud Run Job ({CLOUD_JOB_NAME} in {region})", times)