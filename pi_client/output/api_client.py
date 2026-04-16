import requests
import logging
import time
import threading
from queue import Queue

class APIClient:
    """
    Centralized HTTP client for communication with the FastAPI backend.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.logger = logging.getLogger("APIClient")
        self.session = requests.Session()
        
        # Endpoints
        self.snapshot_url = f"{self.base_url}/vision/snapshots"
        self.event_url = f"{self.base_url}/vision/events"

        # Async handling
        self.queue = Queue(maxsize=10) # Don't buffer too many
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def _worker(self):
        while True:
            item = self.queue.get()
            if item is None: break
            url, payload = item
            try:
                self.session.post(url, json=payload, timeout=2.0)
            except Exception as e:
                self.logger.error(f"Async send error: {e}")
            self.queue.task_done()

    def send_snapshot(self, payload: dict) -> bool:
        """Sends a state snapshot to the backend (Non-blocking)."""
        try:
            if not self.queue.full():
                self.queue.put_nowait((self.snapshot_url, payload))
            return True
        except Exception:
            return False

    def send_event(self, payload: dict) -> bool:
        """Sends a discrete event to the backend (Blocking - rare)."""
        try:
            response = self.session.post(self.event_url, json=payload, timeout=2.0)
            return response.status_code == 201
        except Exception as e:
            self.logger.error(f"Error sending event: {e}")
            return False
            
    def ensure_session(self, session_id: str) -> bool:
        """Ensures the session exists in the backend database (Blocking - startup)."""
        try:
            url = f"{self.base_url}/sessions"
            payload = {
                "id": session_id,
                "start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            response = self.session.post(url, json=payload, timeout=5.0)
            return response.status_code in (200, 201)
        except Exception as e:
            self.logger.error(f"Error ensuring session: {e}")
            return False
    def finalize_session(self, session_id: str, summary: dict) -> bool:
        """Sends the final session summary and stats to the backend database."""
        try:
            url = f"{self.base_url}/sessions/{session_id}/finalize"
            # Some backends might use POST /sessions/summary or similar.
            # We'll use this specific path for production-like behavior.
            response = self.session.post(url, json=summary, timeout=5.0)
            return response.status_code in (200, 201)
        except Exception as e:
            self.logger.error(f"Error finalizing session: {e}")
            return False
