import os
import subprocess


def download_videos(cookies_path, links_file_path):
    resources_path = "./resources"
    folder_name = None

    if not os.path.exists(cookies_path):
        raise FileNotFoundError(f"Cookies file not found: {cookies_path}")

    if not os.path.exists(links_file_path):
        raise FileNotFoundError(f"Links file not found: {links_file_path}")

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

            # Create the folder if it doesn't exist
            os.makedirs(folder_path, exist_ok=True)

            # Execute the yt-dlp command
            output_path = os.path.join(folder_path, f"{name}.%(ext)s")
            command = [
                "yt-dlp",
                "--cookies",
                os.path.abspath(cookies_path),
                link,
                "-o",
                os.path.abspath(output_path),
            ]

            try:
                # Create the folder if it doesn't exist
                os.makedirs(folder_path, exist_ok=True)
                subprocess.run(command, check=True)
                print(
                    f" - {command} -->  Downloaded: {link} to {folder_path} as {name}"
                )
            except subprocess.CalledProcessError as e:
                print(f"Failed to download {link}: {e}")
