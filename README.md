# OMEROAgent

MCP access pattern for OMERO image repositories, project/dataset/image metadata, and web/API endpoint inspection for microscopy data review.

This repository follows the BioRouter `.brxt` extension convention used by `SPOKEAgent` and `UCSFOMOPAgent`: a root `manifest.json`, Python package under `src/`, and optional bundled skills under `skills/`.

## Tools

- `get_omeroagent_status`: report configured environment variables without revealing secrets.
- `get_omeroagent_request_plan`: explain whether an API request is read-only or requires explicit mutation approval.
- `call_omeroagent_api`: call a platform API endpoint with write methods blocked unless `allow_mutation=true`.
- `summarize_omeroagent_resource`: summarize a JSON export or API payload without making a network call.

## Configuration

| Variable | Required | Secret | Purpose |
|---|---:|---:|---|
| `OMERO_BASE_URL` | true | false | OMERO web/API base URL |
| `OMERO_USERNAME` | false | true | OMERO username if the server requires basic auth or token exchange |
| `OMERO_PASSWORD` | false | true | OMERO password or token if the server requires it |
| `OMERO_LOG_LEVEL` | false | false | Logging level |


## Build

```bash
uv sync
scripts/build_brxt.sh
```

The bundle is written to `dist/omeroagent.brxt`.

## Install in BioRouter

```bash
biorouter extension install dist/omeroagent.brxt
```

Add the required secrets with `--secret KEY=value` or configure them in the BioRouter UI.

## License

Apache-2.0. See `LICENSE`.
