"""OMEROAgent MCP server."""

from __future__ import annotations

import base64
import json
import logging
import os
from typing import Any, Literal

import httpx
from fastmcp.exceptions import ToolError
from fastmcp.server import FastMCP
from fastmcp.tools.tool import TextContent, ToolResult
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field

logger = logging.getLogger("OMEROAgent")

READ_METHODS = {"GET", "HEAD", "OPTIONS"}
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class OmeroagentConfig(BaseModel):
    """Runtime configuration for OMEROAgent."""

    base_url: str = Field(default_factory=lambda: os.getenv("OMERO_BASE_URL", "https://omero.example.org"))
    log_level: str = Field(default_factory=lambda: os.getenv("OMERO_LOG_LEVEL", "INFO"))


def _configured_env(keys: list[str]) -> dict[str, bool]:
    return {key: bool(os.getenv(key)) for key in keys}


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/json", "User-Agent": "BioRouter-omeroagent/0.1"}
    token = os.getenv("OMERO_PASSWORD")
    if not token:
        return headers
    auth_header = "BasicOptional"
    if auth_header == "Basic":
        encoded = base64.b64encode((token + ":").encode()).decode()
        headers["Authorization"] = f"Basic {encoded}"
    elif auth_header in {"Bearer", "BearerOptional"}:
        headers["Authorization"] = f"Bearer {token}"
    elif auth_header == "Modal":
        token_id = os.getenv("MODAL_TOKEN_ID", "")
        headers["Authorization"] = f"Token {token_id}:{token}"
    return headers


def _join_url(base_url: str, path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def _result(payload: Any) -> ToolResult:
    return ToolResult(content=[TextContent(type="text", text=json.dumps(payload, indent=2, sort_keys=True))])


def create_server(config: OmeroagentConfig) -> FastMCP:
    logging.basicConfig(level=getattr(logging, config.log_level.upper(), logging.INFO))
    mcp = FastMCP("OMEROAgent")

    @mcp.tool(
        name="get_omeroagent_status",
        annotations=ToolAnnotations(
            title="Get OMEROAgent configuration status",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        ),
    )
    def get_status() -> ToolResult:
        """Report which required credentials are configured without revealing secrets."""
        return _result({
            "service": "OMERO",
            "base_url": config.base_url,
            "documentation": "https://omero-guides.readthedocs.io",
            "configured_env": _configured_env(["OMERO_BASE_URL", "OMERO_USERNAME", "OMERO_PASSWORD", "OMERO_LOG_LEVEL"]),
            "read_methods": sorted(READ_METHODS),
            "write_methods_blocked_by_default": sorted(WRITE_METHODS),
        })

    @mcp.tool(
        name="get_omeroagent_request_plan",
        annotations=ToolAnnotations(
            title="Plan a OMERO API request safely",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        ),
    )
    def request_plan(
        path: str = Field(description="API path or full URL to inspect."),
        method: str = Field(default="GET", description="HTTP method to evaluate."),
    ) -> ToolResult:
        """Return a safety plan before calling a platform API endpoint."""
        method_upper = method.upper()
        return _result({
            "url": _join_url(config.base_url, path),
            "method": method_upper,
            "is_read_method": method_upper in READ_METHODS,
            "requires_allow_mutation": method_upper in WRITE_METHODS,
            "credential_present": bool(os.getenv("OMERO_PASSWORD")),
            "examples": ["/api/", "/webclient/api/datasets/", "/webclient/api/images/"],
            "guidance": "Use read-only calls first. For write, launch, delete, upload, or notebook-edit operations, ask the user for explicit confirmation and pass allow_mutation=true.",
        })

    @mcp.tool(
        name="call_omeroagent_api",
        annotations=ToolAnnotations(
            title="Call a guarded OMERO API endpoint",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        ),
    )
    def call_api(
        path: str = Field(description="API path or full URL."),
        method: Literal["GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"] = Field(default="GET"),
        query: dict[str, Any] | None = Field(default=None, description="Query parameters."),
        json_body: dict[str, Any] | None = Field(default=None, description="JSON body for non-GET calls."),
        allow_mutation: bool = Field(default=False, description="Must be true for POST/PUT/PATCH/DELETE requests."),
        timeout_s: float = Field(default=30.0, ge=1.0, le=120.0, description="HTTP timeout in seconds."),
    ) -> ToolResult:
        """Call the configured platform API with write operations blocked by default."""
        method_upper = method.upper()
        if method_upper in WRITE_METHODS and not allow_mutation:
            raise ToolError(f"{method_upper} requests can mutate OMERO. Re-run only after explicit user confirmation with allow_mutation=true.")
        url = _join_url(config.base_url, path)
        try:
            with httpx.Client(timeout=timeout_s, follow_redirects=True) as client:
                response = client.request(method_upper, url, params=query, json=json_body, headers=_headers())
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type.lower():
                body: Any = response.json()
            else:
                text = response.text
                body = text[:20000] + ("...(truncated)" if len(text) > 20000 else "")
            return _result({
                "url": str(response.url),
                "status_code": response.status_code,
                "ok": response.is_success,
                "content_type": content_type,
                "body": body,
            })
        except httpx.HTTPError as exc:
            raise ToolError(f"OMERO API request failed: {exc}") from exc

    @mcp.tool(
        name="summarize_omeroagent_resource",
        annotations=ToolAnnotations(
            title="Summarize a OMERO resource payload",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        ),
    )
    def summarize_resource(
        payload: dict[str, Any] = Field(description="A JSON object returned by OMERO or pasted from an export."),
    ) -> ToolResult:
        """Summarize common resource fields without making a network call."""
        keys = list(payload.keys())
        preview = {key: payload[key] for key in keys[:20]}
        return _result({
            "service": "OMERO",
            "top_level_keys": keys,
            "preview": preview,
            "provenance_fields_present": [k for k in keys if k.lower() in {"id", "name", "created_at", "updated_at", "owner", "author", "version", "doi", "url"}],
        })

    return mcp


def main(transport: Literal["stdio", "sse", "http"] = "stdio", log_level: str | None = None) -> None:
    config = OmeroagentConfig(log_level=log_level or os.getenv("OMERO_LOG_LEVEL", "INFO"))
    logger.info("Starting OMEROAgent")
    create_server(config).run()


if __name__ == "__main__":
    main()
