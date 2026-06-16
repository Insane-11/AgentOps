from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class OrgIsolationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(("/health", "/docs", "/openapi.json", "/api/auth/login")):
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        return await call_next(request)
