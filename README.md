# OMEROAgent

Retired. This extension no longer calls OMERO and only reports that it is retired. Remove it.

Current version: **0.2.0**

> **Retired.** OMEROAgent was retired on 2026-11-22 and no longer calls any service. Why: OMERO.web logs in with a session and a CSRF token against your own server. This extension sent Basic authentication to a placeholder address, so it never worked, and no OMERO account was available to test a rebuild. Use instead: Browse your images in OMERO.web in the browser, and use the microscopy-image-analysis skill in BAAM to analyse images you export.

This is the final release of a retired Biorouter extension. It replaces every
earlier tool with one, `omero_status`, which shows the notice above. It holds no
credentials, reads no setting and calls no service. Remove the extension in
Biorouter once you no longer need the notice.

## Tools

- `omero_status`: shows why OMEROAgent was retired and what to use instead. It calls no service.

## Bundled skills

Every skill an earlier release bundled is kept, and each now says where its content
moved. An update never deletes a file an earlier version installed, so keeping the
paths is what replaces the old instructions.

## Develop and release

```bash
uv sync
uv run python -m unittest discover -s tests -v
uv run python scripts/build_brxt.py
```

Do not edit `src/omeroagent/_kit/` or `tests/kit_testing/`: they are vendored from the BRXT
adapter kit in the Biorouter repository (`scripts/brxt-adapter-kit/`).

## License

Apache-2.0. See `LICENSE` and `NOTICE`.
