#!/usr/bin/env python3
"""
🚀 Sonatype IQ Server Raw Report Fetcher
Entry point for the application.
"""

import sys
from iq_fetcher.config import Config
from iq_fetcher.fetcher import RawReportFetcher
from iq_fetcher.utils import logger, ErrorHandler, IQServerError


@ErrorHandler.handle_config_error
def main() -> None:
    """🚀 Main entry point - Let's fetch some reports!"""
    try:
        logger.info("🔧 Loading configuration...")
        config = Config.from_env()

        logger.info("🎯 Initializing report fetcher...")
        fetcher = RawReportFetcher(config)

        fetcher.fetch_all_reports()

    except KeyboardInterrupt:
        logger.warning("⏹️  Cancelled by user - See you next time!")
        sys.exit(0)
    except (ValueError, IQServerError) as e:
        logger.error(f"💥 Configuration/Server error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)


def run():
    """Entry point with welcome messages."""
    logger.info("🚀 Welcome to the Sonatype IQ Server Raw Report Fetcher!")
    logger.info("=" * 60)
    main()


if __name__ == "__main__":
    run()
