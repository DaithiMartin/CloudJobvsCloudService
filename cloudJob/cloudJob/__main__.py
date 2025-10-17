import os
import sys

from src.run import main

# run inference job
if __name__ == '__main__':
    # Get the unique execution ID from the environment
    execution_id = os.getenv("CLOUD_RUN_EXECUTION", "unknown")

    # This is the first thing that runs. The format is critical for the script.
    print(f"JOB_CONTAINER_STARTED_LOG:{execution_id}")
    sys.stdout.flush()  # Ensure the log is sent immediately

    main()