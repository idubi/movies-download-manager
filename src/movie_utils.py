import os
import asyncio


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


async def download_videos_async(
    cookies_path, links_file_path, max_concurrent_downloads=5
):
    """
    Asynchronously download multiple videos with a limit on concurrent downloads.
    """
    resources_path = "./resources"
    folder_name = None

    if not os.path.exists(cookies_path):
        raise FileNotFoundError(f"Cookies file not found: {cookies_path}")

    if not os.path.exists(links_file_path):
        raise FileNotFoundError(f"Links file not found: {links_file_path}")

    # Read links and prepare tasks
    tasks = []
    semaphore = asyncio.Semaphore(max_concurrent_downloads)

    async def semaphore_wrapper(cookies_path, link, name, folder_path):
        async with semaphore:
            await download_video(cookies_path, link, name, folder_path)

    with open(links_file_path, "r") as links_file:
        for line in links_file:
            line = line.strip()
            if not line:
                continue

            # Check if the line specifies the folder name
            if line.startswith("folder:"):
                folder_name = line.split("folder:")[1].strip()
                continue

            # Ensure a folder name has been set
            if not folder_name:
                print("Skipping links because no folder name is specified.")
                continue

            # Parse the link and name
            parts = line.split()
            if len(parts) != 2:
                print(f"Skipping invalid line: {line}")
                continue

            link, name = parts
            folder_path = os.path.join(resources_path, folder_name)

            # Add the task to the list
            tasks.append(semaphore_wrapper(cookies_path, link, name, folder_path))

    # Run all tasks concurrently with a limit on the number of concurrent downloads
    await asyncio.gather(*tasks)
