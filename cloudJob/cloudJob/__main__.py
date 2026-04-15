# import os
# import sys
#
# from src.run import main
#
# # run inference job
# if __name__ == '__main__':
#     # Get the unique execution ID from the environment
#     execution_id = os.getenv("CLOUD_RUN_EXECUTION", "unknown")
#
#     # This is the first thing that runs. The format is critical for the script.
#     print(f"JOB_CONTAINER_STARTED_LOG:{execution_id}")
#     sys.stdout.flush()  # Ensure the log is sent immediately
#
#     main()

import os
import contextlib
import tempfile
from pathlib import Path
import geopandas as gpd
from shapely.geometry import box
import seamless_3dep as sdem

import aiohttp

try:
    from aiohttp_client_cache import CachedSession
except ImportError:
    CachedSession = None


@contextlib.contextmanager
def bypass_waf_user_agent():
    """Spoof User-Agent for aiohttp to bypass USGS CloudFront."""
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    original_aio_request = aiohttp.ClientSession._request
    if CachedSession:
        original_cached_request = CachedSession._request

    async def _patched_aio_request(self, method, str_or_url, **kwargs):
        headers = dict(kwargs.get("headers") or {})
        headers["User-Agent"] = USER_AGENT
        kwargs["headers"] = headers
        return await original_aio_request(self, method, str_or_url, **kwargs)

    async def _patched_cached_request(self, method, str_or_url, **kwargs):
        headers = dict(kwargs.get("headers") or {})
        headers["User-Agent"] = USER_AGENT
        kwargs["headers"] = headers
        return await original_cached_request(self, method, str_or_url, **kwargs)

    try:
        aiohttp.ClientSession._request = _patched_aio_request
        if CachedSession:
            CachedSession._request = _patched_cached_request
        yield
    finally:
        aiohttp.ClientSession._request = original_aio_request
        if CachedSession:
            CachedSession._request = original_cached_request


def main():
    print("Starting USGS Network Isolation Test...")

    # 1. Create a dummy bounding box (Savannah, GA area from your logs)
    bbox = box(-81.730504, 32.025507, -81.711515, 32.046881)
    gdf = gpd.GeoDataFrame({'geometry': [bbox]}, crs="EPSG:4326")
    bounds = gdf.total_bounds

    # 2. Attempt the network call
    print(f"Requesting 3DEP DEM for bounds: {bounds}")
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with bypass_waf_user_agent():
                # Just fetch the map, we don't even need to process it.
                # We just want to see if the HTTP call succeeds.
                list_raster_files = sdem.get_map(
                    "DEM",
                    bounds,
                    Path(tmp_dir),
                    res=30,
                )
        print(f"SUCCESS! Retrieved {len(list_raster_files)} files.")
    except Exception as e:
        print(f"NETWORK FAILURE: {e}")
        # Explicitly exit with error code so Cloud Run flags it
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()