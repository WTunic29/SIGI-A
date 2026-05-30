from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import time

from app.core.logging_config import security_logger


class SecurityLogsMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        start_time = time.time()

        response = await call_next(request)

        process_time = round(time.time() - start_time, 4)

        ip = request.client.host
        method = request.method
        path = request.url.path
        status_code = response.status_code

        user_agent = request.headers.get(
            "user-agent",
            "unknown"
        )

        security_logger.info(
            f"IP={ip} | "
            f"METHOD={method} | "
            f"PATH={path} | "
            f"STATUS={status_code} | "
            f"TIME={process_time}s | "
            f"UA={user_agent}"
        )

        return response