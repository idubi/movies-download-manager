import os
import asyncio
import logging
from collections import defaultdict
from src.const.config_const import (
    KAFKA_CONFIG,
    KAFKA_TOPIC_DOWNLOAD_STATUS,
    KAFKA_TOPIC_DOWNLOAD_REQUESTS,
    MAX_CONCURRENT_DOWNLOADS,
    MAX_CONCURRENT_DOWNLOADS_PER_FOLDER    
)
from src.services.message_HUB.message_hub import MessageHub

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DownloadManager:


    
    def __init__(self, kafka_config=None, request_topic=None, status_topic=None):
        
        self._kafka_config = kafka_config or KAFKA_CONFIG
        self._request_topic = request_topic or KAFKA_TOPIC_DOWNLOAD_REQUESTS
        self._status_topic = status_topic or KAFKA_TOPIC_DOWNLOAD_STATUS
        self.message_hub = MessageHub(self._kafka_config)
        
        # Add concurrent download management
        self.max_concurrent = MAX_CONCURRENT_DOWNLOADS
        self.active_downloads = defaultdict(int)
        self.total_active_downloads = 0  # Add this line to initialize the counter
        self.folder_semaphores = {}
        self.global_semaphore = asyncio.Semaphore(self.max_concurrent)
        self.lock = asyncio.Lock()  # Add lock for thread-safe counting
        print(f"Initializing Download Manager with max concurrent downloads: {self.max_concurrent}")
        logger.info(f"Max concurrent downloads per folder: {MAX_CONCURRENT_DOWNLOADS_PER_FOLDER}")


    async def _download_video(self, cookies_path, link, name, folder_path):
        os.makedirs(folder_path, exist_ok=True)
        output_path = os.path.join(folder_path, f"{name}.%(ext)s")
        command = ["yt-dlp"]
        if cookies_path:
            command += ["--cookies", os.path.abspath(cookies_path)]
        command += [link, "-o", os.path.abspath(output_path)]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return f"SUCCESS: {link} downloaded to {folder_path} as {name}"
        else:
            return f"FAILED: {link} - {stderr.decode().strip()}"

     

    async def _process_task(self, task):
        folder_name = task["folder_name"]
        max_concurrent = min(
            task.get("max_concurrent", MAX_CONCURRENT_DOWNLOADS_PER_FOLDER),
            self.max_concurrent
        )
        
        if folder_name not in self.folder_semaphores:
            self.folder_semaphores[folder_name] = asyncio.Semaphore(max_concurrent)

        try:
            # Get lock before incrementing counters
            async with self.lock:
                if (self.total_active_downloads >= self.max_concurrent or 
                    self.active_downloads[folder_name] >= max_concurrent):
                    print(f"Skipping task - at limit. Total: {self.total_active_downloads}, Folder {folder_name}: {self.active_downloads[folder_name]}")
                    return

                self.active_downloads[folder_name] += 1
                self.total_active_downloads += 1
                current_folder_count = self.active_downloads[folder_name]
                current_total = self.total_active_downloads
                print(f"Starting download in {folder_name}. Active: {current_folder_count}")
                print(f"Total active downloads: {current_total}")

            # Process download
            async with self.global_semaphore, self.folder_semaphores[folder_name]:
                link = task["link"]
                name = task["name"]
                folder_path = os.path.join("./resources", folder_name)
                cookies_path = task.get("cookies_path") if task.get("need_authentication") else None

                status = await self._download_video(cookies_path, link, name, folder_path)
                self.message_hub.send_message(self._status_topic, key=name, value={"status": status})

        except Exception as e:
            error_message = f"Error processing task: {str(e)}"
            print(error_message)
            self.message_hub.send_message(
                self._status_topic, 
                key=task.get("name", "unknown"), 
                value={"status": error_message}
            )
        finally:
            # Get lock before decrementing counters
            async with self.lock:
                if self.active_downloads[folder_name] > 0:
                    self.active_downloads[folder_name] -= 1
                if self.total_active_downloads > 0:
                    self.total_active_downloads -= 1
                print(f"Completed download in {folder_name}. Active: {self.active_downloads[folder_name]}")
                print(f"Total active downloads: {self.total_active_downloads}")

            
    async def process_messages(self, messages):
        tasks = []
        folder_counts = defaultdict(int)
        
        # Group messages by folder and respect folder limits
        for message in messages:
            folder_name = message["folder_name"]
            folder_limit = message.get("max_concurrent", MAX_CONCURRENT_DOWNLOADS_PER_FOLDER)
            
            if (folder_counts[folder_name] < folder_limit and 
                len(tasks) < self.max_concurrent):
                tasks.append(self._process_task(message))
                folder_counts[folder_name] += 1
        
        if tasks:
            logger.info(f"Starting {len(tasks)} concurrent downloads")
            await asyncio.gather(*tasks)
        else:
            logger.info("No slots available for downloads, waiting...")
            await asyncio.sleep(1)   
            
    async def run(self):
        logger.info("Download Manager run starting...")
        try:
            messages_buffer = []
            batch_size = self.max_concurrent
            logger.info(f"Starting to consume messages from topic: {self._request_topic} with batch size {batch_size}")
            
            async for message in self.message_hub.consume_messages_async(
                self._request_topic,
                group_id="download-manager-group"
            ):
                messages_buffer.append(message)
                logger.info(f"Received message. Buffer size: {len(messages_buffer)}")
                
                # Only process when we have a full batch
                if len(messages_buffer) >= batch_size:
                    logger.info(f"Processing full batch of {len(messages_buffer)} messages")
                    await self.process_messages(messages_buffer)
                    messages_buffer = []
                    
                # Don't process partial batches immediately - removed the elif block
                
            # Process any remaining messages at the end
            if messages_buffer:
                logger.info(f"Processing final batch of {len(messages_buffer)} messages")
                await self.process_messages(messages_buffer)
                        
        except Exception as e:
            logger.error(f"Error in run method: {str(e)}", exc_info=True)
            raise



if __name__ == "__main__":
    manager = DownloadManager()
    asyncio.run(manager.run())