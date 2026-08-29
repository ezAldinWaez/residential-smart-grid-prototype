"""Run the browser-based RSGP dashboard."""

import os

from dotenv import load_dotenv
import uvicorn


def main() -> None:
    """Start the local dashboard web server."""
    load_dotenv()
    host = os.getenv("RSGP_DASHBOARD_HOST", "127.0.0.1")
    port = int(os.getenv("RSGP_DASHBOARD_PORT", 8085))
    uvicorn.run("dashboard.app:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
