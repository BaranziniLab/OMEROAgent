---
name: omero-imaging-data
description: "Retired with OMEROAgent. This skill no longer holds instructions."
---

# omero-imaging-data has moved

This skill was bundled with OMEROAgent, which is retired. OMEROAgent never reached an OMERO server: OMERO.web needs a session login that the extension did not perform. Browse your images in OMERO.web in the browser, and use the `microscopy-image-analysis` skill from BAAM to analyse images you export. Remove OMEROAgent from Biorouter.

OMEROAgent was retired on 2026-11-22 and no longer calls any service. Why: OMERO.web logs in with a session and a CSRF token against your own server. This extension sent Basic authentication to a placeholder address, so it never worked, and no OMERO account was available to test a rebuild. Use instead: Browse your images in OMERO.web in the browser, and use the microscopy-image-analysis skill in BAAM to analyse images you export.
