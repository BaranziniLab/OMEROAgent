"""Command-line entry point for OMEROAgent."""

import logging
import os

from omeroagent.server import main as server_main

logger = logging.getLogger("OMEROAgent")


def main() -> None:
    log_level = os.getenv("OMERO_LOG_LEVEL", "INFO")
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO))
    logger.info("Starting OMEROAgent")
    server_main(log_level=log_level)


if __name__ == "__main__":
    main()
