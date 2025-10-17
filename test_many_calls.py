import requests
import time

# --- Configuration ---
SERVICE_URL = "https://cloud-service-418100612281.us-west1.run.app"
NUM_RUNS = 50


def main():
    """
    Main function to run the experiment.
    """
    if "your-public-service-name" in SERVICE_URL:
        print("🔴 ERROR: Please update the 'SERVICE_URL' variable in the script with your actual Cloud Run URL.")
        return

    print(f"🚀 Starting experiment: Hitting {SERVICE_URL} {NUM_RUNS} times...")

    run_times = []
    total_start_time = time.monotonic()

    for i in range(1, NUM_RUNS + 1):
        run_start_time = time.monotonic()
        try:
            # Make a simple GET request to the public Cloud Run service
            response = requests.get(SERVICE_URL, timeout=30)
            print(response.text)
            # Check for HTTP errors (e.g., 404, 500)
            response.raise_for_status()

            run_end_time = time.monotonic()
            duration = run_end_time - run_start_time
            run_times.append(duration)
            print(f"✅ Run #{i:02d}: {duration:.4f} seconds (Status: {response.status_code})")

        except requests.exceptions.RequestException as e:
            print(f"❌ Run #{i:02d}: FAILED - {e}")

    total_end_time = time.monotonic()
    total_duration = total_end_time - total_start_time

    print("\n" + "=" * 40)
    print("📊 Experiment Complete: Summary")
    print("=" * 40)

    if run_times:
        print(f"⏱️  Total time for {len(run_times)} successful runs: {total_duration:.4f} seconds")
        print(f" slowest run:  {max(run_times):.4f} seconds")
        print(f" fastest run: {min(run_times):.4f} seconds")
        print(f" average run:  {(sum(run_times) / len(run_times)):.4f} seconds")
    else:
        print("No successful runs to analyze.")


if __name__ == "__main__":
    main()