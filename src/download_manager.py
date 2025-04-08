from message_hub import MessageHub
import asyncio
import os


async def download_video(cookies_path, link, name, folder_path):
    """
    Asynchronously download a video using yt-dlp.
    """
    os.makedirs(folder_path, exist_ok=True)
    output_path = os.path.join(folder_path, f"{name}.%(ext)s")
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
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        return f"SUCCESS: {link} downloaded to {folder_path} as {name}"
    else:
        return f"FAILED: {link} - {stderr.decode().strip()}"


async def process_task(task, cookies_path, message_hub, status_topic):
    """
    Processes a single download task.
    """
    link = task["link"]
    name = task["name"]
    folder_name = task["folder_name"]
    folder_path = os.path.join("./resources", folder_name)

    # Execute the download
    status = await download_video(cookies_path, link, name, folder_path)

    # Publish the status to the status topic
    message_hub.send_message(status_topic, key=name, value={"status": status})


if __name__ == "__main__":
    # Kafka configuration
    kafka_config = {
        "bootstrap.servers": "localhost:9092",  # Replace with your Kafka server
    }
    kafka_topic = "download-requests"
    status_topic = "download-status"

    # Initialize the Message Hub
    message_hub = MessageHub(kafka_config)

    # Path to cookies file
    cookies_path = "./resources/cookies.txt"

    # Consume tasks from Kafka
    def handle_task(task):
        asyncio.run(process_task(task, cookies_path, message_hub, status_topic))

    message_hub.consume_messages(
        kafka_topic, group_id="download-manager-group", callback=handle_task
    )
