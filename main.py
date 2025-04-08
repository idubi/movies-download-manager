import asyncio
from src.cookies_authentication import (
    create_cookies_from_browser_cookies,
    save_cookies_to_file,
)
from src.movie_utils import download_videos_async
from src.config_manager import read_links_file


browser_cookies_file_path = "./resources/raw-cookies.txt"
cookies_file_path = "./resources/cookies.txt"
links_file_path = "./resources/links-tests.txt"
max_concurrent_downloads = 5


if __name__ == "__main__":
    # Step 1: Create cookies file
    cookies_collection = create_cookies_from_browser_cookies(browser_cookies_file_path)
    save_cookies_to_file(cookies_collection, cookies_file_path)
    print(f"Cookies file created at: {cookies_file_path}")

    # Step 2: Read links file
    tasks = read_links_file(links_file_path)
    print(f"Loaded {len(tasks)} tasks from links file.")

    # Step 3: Start downloads
    asyncio.run(
        download_videos_async(cookies_file_path, tasks, max_concurrent_downloads)
    )

    print("All downloads completed.")
