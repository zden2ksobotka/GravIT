# Page Statistics Plugin

This plugin provides a lightweight and efficient way to track page view counts for the website. It operates in the background without requiring any user-facing configuration.

## How it Works

The plugin uses a combination of FastAPI Middleware and background tasks to count and store statistics.

1.  **Middleware:** It registers a `StatisticsMiddleware` with the main application. This middleware intercepts every successful HTML page response (`status_code == 200`). For each such response, it increments a counter for the corresponding page slug in a global Python dictionary (`PAGE_VIEWS`). This in-memory counting is extremely fast and has a negligible impact on performance.

2.  **Persistent Storage:** To prevent data loss on application restart, the statistics are periodically saved to a file.
    -   **File Location:** The data is stored in a text file directly within the plugin's directory (`user/plugin/page_statistics/`).
    -   **File Naming:** The file is named `stats_<hostname>_<pid>.txt` (e.g., `stats_cms.n0ip.eu_12345.txt`). This per-process naming convention prevents conflicts when running multiple Uvicorn workers.
    -   **Format:** The file contains simple lines of text, with each line holding a `slug` and its `count`, separated by a space.

3.  **Asynchronous Saving:** A background task (`asyncio.create_task`) is initiated on startup, which saves the in-memory `PAGE_VIEWS` dictionary to the corresponding file at a regular interval. This interval is configurable.

4.  **Data Loading & Merging:** On application startup, the plugin reads all `stats_*.txt` files that match its hostname. It merges the data from all worker processes to create a consolidated view count, ensuring that statistics are aggregated even when the application runs with multiple workers.

## Configuration

The save interval can be configured in the following file:
`user/plugin/page_statistics/page_statistics_config.py`

-   **`STATS_REFRESH_SECONDS`**: The interval in seconds at which the statistics are saved to disk. The default is `300` seconds (5 minutes).
