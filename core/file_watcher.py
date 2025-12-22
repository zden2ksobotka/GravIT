import time
import logging
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class ContentChangeHandler(FileSystemEventHandler):
    """A handler for filesystem events that triggers a content reload."""

    def __init__(self, reload_callback):
        super().__init__()
        self.reload_callback = reload_callback
        self._debounce_time = 1.0  # 1 second
        self._last_event_time = 0

    def _should_trigger(self):
        """Debounce events to avoid rapid reloads."""
        current_time = time.time()
        if (current_time - self._last_event_time) > self._debounce_time:
            self._last_event_time = current_time
            return True
        return False

    def on_any_event(self, event):
        """
        Catches all events and triggers a reload if it's a relevant change.
        - Ignores directory events (we only care about file changes).
        - Ignores events from hidden files/directories (like .git, __pycache__).
        """
        if event.is_directory:
            return
        
        # Ignore hidden files and common temporary files
        path_part = event.src_path.split(os.sep)
        if any(part.startswith('.') for part in path_part) or event.src_path.endswith('~'):
            return

        if self._should_trigger():
            logger.debug(f"[File Watcher] Change detected: {event.event_type} on {event.src_path}. Triggering content reload.")
            self.reload_callback()

def start_watcher(paths_to_watch, reload_callback):
    """
    Initializes and starts the filesystem observer in a background thread.
    
    :param paths_to_watch: A list of directory/file paths to monitor.
    :param reload_callback: The function to call when a change is detected.
    :return: The observer instance.
    """
    event_handler = ContentChangeHandler(reload_callback)
    observer = Observer()
    for path in paths_to_watch:
        if os.path.exists(path):
            observer.schedule(event_handler, path, recursive=True)
            logger.info(f"Watching for changes in: {path}")
        else:
            logger.warning(f"Path not found, not watching: {path}")
            
    observer.start()
    logger.info("File watcher started in background thread.")
    return observer
