---
name: omero-imaging-data
description: Use OMEROAgent when working with OMERO platform data, API resources, provenance, or reproducibility checks from inside BioRouter.
license: Apache-2.0
user-invocable: false
---

# OMEROAgent Skill

Use this extension to inspect OMERO project, dataset, image, and annotation endpoints. Keep downloads scoped and avoid PHI-bearing image exports unless permitted.

## Operating rules

- Start with `get_omeroagent_status` to confirm whether credentials and base URLs are configured.
- Use `get_omeroagent_request_plan` before any endpoint that may create, update, launch, upload, or delete a resource.
- Prefer read-only `GET` requests through `call_omeroagent_api` while exploring.
- Do not pass `allow_mutation=true` unless the user has explicitly approved the exact operation, target resource, and expected side effect.
- Preserve platform IDs, versions, owners/authors, timestamps, and URLs in any report.
- Never print API tokens, passwords, bearer headers, or session cookies.

## Useful starting endpoints

- `/api/`
- `/webclient/api/datasets/`
- `/webclient/api/images/`
