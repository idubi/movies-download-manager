import os
import asyncio
import time


async def download_video(cookies_path, link, name, folder_path):
    """
    Asynchronously download a video using yt-dlp.
    """
    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)

    # Construct the yt-dlp command
    output_path = os.path.join(folder_path, f"{name}.%(ext)s")
    command = [
        "yt-dlp",
        "--cookies",
        os.path.abspath(cookies_path),
        link,
        "-o",
        os.path.abspath(output_path),
    ]

    # Run the command asynchronously
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    # Handle the result
    if process.returncode == 0:
        print(f"SUCCESS: {link} downloaded to {folder_path} as {name}")
    else:
        print(f"FAILED: {link} - {stderr.decode().strip()}")


async def download_videos_async(cookies_path, tasks, max_concurrent_downloads=5):
    """
    Asynchronously download multiple videos with a limit on concurrent downloads.
    """
    resources_path = "./resources"
    semaphore = asyncio.Semaphore(max_concurrent_downloads)

    async def semaphore_wrapper(cookies_path, link, name, folder_path):
        async with semaphore:
            await download_video(cookies_path, link, name, folder_path)

    # Group tasks by folder
    tasks_by_folder = {}
    for task in tasks:
        folder_name = task["folder_name"]
        if folder_name not in tasks_by_folder:
            tasks_by_folder[folder_name] = []
        tasks_by_folder[folder_name].append(task)

    # Check for duplicate file names in each folder
    for folder_name, folder_tasks in tasks_by_folder.items():
        folder_path = os.path.join(resources_path, folder_name)
        file_names = [
            task.get("name") or f"default_{int(time.time())}" for task in folder_tasks
        ]
        if len(file_names) != len(set(file_names)):
            print(
                f"ERROR: Duplicate file names detected in folder '{folder_name}'. Aborting downloads for this folder."
            )
            continue

        # Prepare and run tasks for the folder
        download_tasks = []
        for task in folder_tasks:
            link = task["link"]
            name = (
                task.get("name") or f"default_{int(time.time())}"
            )  # Assign default name if not provided
            download_tasks.append(
                semaphore_wrapper(cookies_path, link, name, folder_path)
            )

        # Run all tasks concurrently with a limit on the number of concurrent downloads
        await asyncio.gather(*download_tasks)
