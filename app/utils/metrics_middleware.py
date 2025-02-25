import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from collections import defaultdict

logger = logging.getLogger(__name__)

class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.metrics = defaultdict(lambda: {"count": 0, "success": 0, "failure": 0})

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = None
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            process_time = time.time() - start_time
            endpoint = request.url.path
            self.metrics[endpoint]["count"] += 1
            if status_code < 400:
                self.metrics[endpoint]["success"] += 1
            else:
                self.metrics[endpoint]["failure"] += 1
            logger.info(f"Request to {endpoint} took {process_time:.4f} seconds, status code: {status_code}")
        return response

    def get_metrics(self):
        return self.metrics