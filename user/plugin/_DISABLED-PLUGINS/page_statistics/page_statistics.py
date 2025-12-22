import asyncio
import logging
from fastapi import Request
import os
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path
import aiofiles
from datetime import datetime

# --- Configuration ---
try:
    from user.plugin.page_statistics.page_statistics_config import STATS_REFRESH_SECONDS
except ImportError:
    STATS_REFRESH_SECONDS = 300

# --- Globals ---
logger = None # Will be set by register_routes
PAGE_VIEWS = {}
STATS_FILE_PATH = None
lock = asyncio.Lock()
plugin_dir = Path(__file__).parent.resolve()

# --- Core Functions ---
async def load_stats():
    """Loads stats from the shared STATS_FILE_PATH into the worker's PAGE_VIEWS."""
    global PAGE_VIEWS
    PAGE_VIEWS.clear()

    if not STATS_FILE_PATH.is_file():
        logger.info("No shared stats file found. Starting with empty stats for this worker.")
        return

    async with lock: # Ensure exclusive access during file read
        try:
            logger.info(f"Loading shared stats from: {STATS_FILE_PATH}")
            async with aiofiles.open(STATS_FILE_PATH, mode='r', encoding='utf-8') as f:
                async for line in f:
                    parts = line.strip().split()
                    if len(parts) == 2 and parts[1].isdigit():
                        slug = parts[0]
                        count = int(parts[1])
                        PAGE_VIEWS[slug] = count # Initialize worker's view with shared data
            logger.info(f"Successfully loaded {len(PAGE_VIEWS)} entries from {STATS_FILE_PATH} into worker's cache.")
        except Exception as e:
            logger.error(f"Failed to load shared statistics from {STATS_FILE_PATH}: {e}", exc_info=True)

async def save_stats():
    """Aggregates worker's PAGE_VIEWS with shared stats and saves to STATS_FILE_PATH."""
    global PAGE_VIEWS
    if not STATS_FILE_PATH:
        logger.warning("Cannot save stats, STATS_FILE_PATH is not set yet.")
        return

    async with lock: # Ensure exclusive access during file operations
        try:
            # 1. Read existing shared stats
            shared_stats = {}
            if STATS_FILE_PATH.is_file():
                async with aiofiles.open(STATS_FILE_PATH, mode='r', encoding='utf-8') as f:
                    async for line in f:
                        parts = line.strip().split()
                        if len(parts) == 2 and parts[1].isdigit():
                            slug = parts[0]
                            count = int(parts[1])
                            shared_stats[slug] = count

            # 2. Merge worker's PAGE_VIEWS into shared_stats
            for slug, count in PAGE_VIEWS.items():
                shared_stats[slug] = shared_stats.get(slug, 0) + count

            # 3. Write combined stats to a temporary file with a unique name per worker
            temp_file_path = STATS_FILE_PATH.with_suffix(f'.{os.getpid()}.tmp')
            
            # Ensure the parent directory for the stats file exists
            STATS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(temp_file_path, mode='w', encoding='utf-8') as f:
                for slug, count in shared_stats.items():
                    await f.write(f"{slug} {count}\n")
            
            # 4. Atomically replace the old file with the new one
            # Use os.replace for atomicity and to handle cases where the target might not exist.
            try:
                os.replace(temp_file_path, STATS_FILE_PATH)
            except FileNotFoundError:
                logger.error(f"Worker {os.getpid()}: Temporary file {temp_file_path} not found for os.replace. This should not happen as it's created earlier. Skipping replace.", exc_info=True)
            except Exception as e:
                logger.error(f"Worker {os.getpid()}: Failed to atomically replace statistics file {STATS_FILE_PATH} with {temp_file_path}: {e}", exc_info=True)

            logger.info(f"Worker {os.getpid()}: Successfully aggregated and saved statistics for {len(shared_stats)} pages to {STATS_FILE_PATH}")

            # 5. Clear worker's local PAGE_VIEWS after saving
            PAGE_VIEWS.clear()
            logger.info(f"Worker {os.getpid()}: Cleared local PAGE_VIEWS cache.")

        except Exception as e:
            logger.error(f"Worker {os.getpid()}: Failed to save statistics: {e}", exc_info=True)

async def periodic_save_task():
    """Background task that periodically saves statistics."""
    while True:
        await asyncio.sleep(STATS_REFRESH_SECONDS)
        await save_stats()

# --- Middleware ---
class StatisticsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # We only want to track successful page views (HTML responses)
        if response.status_code == 200 and 'text/html' in response.headers.get('content-type', ''):
            slug = request.url.path.strip('/')
            if not slug: # Handle root path
                slug = "home"

            # --- Increment page view count ---
            async with lock:
                PAGE_VIEWS[slug] = PAGE_VIEWS.get(slug, 0) + 1
                
        return response

# --- Plugin Registration ---
def register_routes(app, templates, theme_config, cms_theme, logger_instance):
    """This function is called by the plugin loader."""
    global logger, STATS_FILE_PATH
    logger = logger_instance
    
    # Determine stats file path early
    import socket
    hostname = socket.gethostname()
    STATS_FILE_PATH = plugin_dir / f"stats_{hostname}.txt"
    logger.info(f"Statistics file path set to: {STATS_FILE_PATH}")

    async def initialize_statistics():
        """A single startup function for the plugin."""
        logger.info("Page Statistics Plugin: Initializing...")
        await load_stats()
        asyncio.create_task(periodic_save_task())
        logger.info(f"Periodic saving task started with an interval of {STATS_REFRESH_SECONDS} seconds.")

    app.add_event_handler("startup", initialize_statistics)
    app.add_event_handler("shutdown", save_stats)
    app.add_middleware(StatisticsMiddleware)
    logger.info("Page Statistics Plugin registered successfully.")
