"""
Injects request_id into request state for log correlation.
"""

import uuid
from fastapi import Request

async def request_context_middleware(request: Request, call_next):
    request.state.request_id = request.headers.get(
        "x-request-id",
        f"req-{uuid.uuid4().hex[:8]}"
    )
    response = await call_next(request)
    return response
