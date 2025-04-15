import os
import asyncio
from src.services.downlaod_manager.cookies_authentication import (
    create_cookies_from_browser_cookies,
    save_cookies_to_file,
)
from src.const.config_const import (
    KAFKA_CONFIG,
    KAFKA_TOPIC_DOWNLOAD_STATUS,
    KAFKA_TOPIC_DOWNLOAD_REQUESTS,
)
from src.services.message_HUB.message_hub import MessageHub


class DownloadManager:
    def __init__(self, kafka_config=None, request_topic=None, status_topic=None):
        self._kafka_config = kafka_config or KAFKA_CONFIG
        self._request_topic = request_topic or KAFKA_TOPIC_DOWNLOAD_REQUESTS
        self._status_topic = status_topic or KAFKA_TOPIC_DOWNLOAD_STATUS
        self.message_hub = MessageHub(self._kafka_config)

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
        try:
            link = task["link"]
            name = task["name"]
            need_cookies = task.get("need_authentication", False)
            cookies_path = None

            folder_name = task["folder_name"]
            folder_path = os.path.join("./resources", folder_name)

            if str(need_cookies).lower() == 'true':
                raw_cookie_path = task["raw_cookies_path"]
                cookies_path = task["cookies_path"]
                cookies = create_cookies_from_browser_cookies(raw_cookie_path)
                save_cookies_to_file(cookies_path, cookies)

            status = await self._download_video(cookies_path, link, name, folder_path)
            self.message_hub.send_message(self._status_topic, key=name, value={"status": status})

        except Exception as e:
            error_message = f"Error processing task: {str(e)}"
            print(error_message)
            self.message_hub.send_message(self._status_topic, key=task.get("name", "unknown"), value={"status": error_message})

    def run(self):
        def handle_task(task):
            asyncio.run(self._process_task(task))

        self.message_hub.consume_messages(
            self._request_topic,
            group_id="download-manager-group",
            callback=handle_task,
        )


if __name__ == "__main__":
    manager = DownloadManager()
    manager.run()
