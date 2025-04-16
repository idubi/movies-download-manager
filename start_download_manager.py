from src.services.downlaod_manager.download_manager import DownloadManager
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("Starting Download Manager Service...")
        manager = DownloadManager()
        
        # Add debug info before run
        logger.info(f"Kafka config: {manager._kafka_config}")
        logger.info(f"Request topic: {manager._request_topic}")
        logger.info(f"Status topic: {manager._status_topic}")
        
        # Wait for Kafka to be ready
        await asyncio.sleep(2)  # Give Kafka time to initialize
        
        logger.info("Starting message consumption...")
        await manager.run()
        
    except KeyboardInterrupt:
        logger.info("Shutting down by user request...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Failed to start Download Manager: {str(e)}")
        raise