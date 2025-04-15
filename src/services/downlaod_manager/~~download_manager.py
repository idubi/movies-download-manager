from cookies_authentication import (
    create_cookies_from_browser_cookies,
    save_cookies_to_file,
)

from src.const.config_const import KAFKA_CONFIG,\
     KAFKA_TOPIC_DOWNLOAD_STATUS , KAFKA_TOPIC_DOWNLOAD_REQUESTS

from src.services.message_HUB.message_hub import MessageHub
import asyncio
import os


async def download_video(cookies_path, link, name, folder_path):
    """
    Asynchronously download a video using yt-dlp.
    """
    os.makedirs(folder_path, exist_ok=True)
    output_path = os.path.join(folder_path, f"{name}.%(ext)s")
    if cookies_path is None:
        command = [
            "yt-dlp",
            link,
            "-o",
            os.path.abspath(output_path),
        ]
    else:
        command = [
            "yt-dlp",
            "--cookies",
            os.path.abspath(cookies_path),
            link,
            "-o",
            os.path.abspath(output_path),
        ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        return f"SUCCESS: {link} downloaded to {folder_path} as {name}"
    else:
        return f"FAILED: {link} - {stderr.decode().strip()}"


async def process_task(task,  message_hub, status_topic):
    """
    Processes a single download task.
    """
    try:
        link = task["link"]
        name = task["name"]
        try: 
            need_cookies = task["need_authentication"] 
        except KeyError:
            need_cookies = False
            cookies_path = None
            
        
        cookies_path = None
        folder_name = task["folder_name"]
        folder_path = os.path.join("./resources", folder_name)
        if str(need_cookies).strip().lower() == 'true':
            raw_cookie_path = task["raw_cookies_path"]
            cookies_path =  task["cookies_path"]
            cookies = create_cookies_from_browser_cookies(raw_cookie_path)
            save_cookies_to_file(cookies_path, cookies)   
            

        # Execute the download
        status = await download_video(cookies_path, link, name, folder_path)

        # Publish the status to the status topic
        message_hub.send_message(status_topic, key=name, value={"status": status})
    except Exception as e:
        error_message = f"Error processing task: {str(e)}"
        print(error_message)
        message_hub.send_message(status_topic, key=name, value={"status": error_message})




if __name__ == "__main__":
    # Kafka configuration
    kafka_config =KAFKA_CONFIG
    kafka_topic = KAFKA_TOPIC_DOWNLOAD_REQUESTS
    status_topic = KAFKA_TOPIC_DOWNLOAD_STATUS

    # Initialize the Message Hub
    message_hub = MessageHub(kafka_config)

    # Consume tasks from Kafka
    def handle_task(task):
        asyncio.run(MessageHub.process_task(task, message_hub, status_topic))

    message_hub.consume_messages(
        kafka_topic, group_id="download-manager-group", callback=handle_task
    )