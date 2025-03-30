import asyncio
from src.cookies_authentication import (
    create_cookies_from_browser_cookies,
    save_cookies_to_file,
)
from src.movie_utils import download_videos_async


browser_cookies_file_path = "./resources/raw-cookies.txt"
cookies_file_path = "./resources/cookies.txt"
links_file_path = "./resources/links-capsule04.txt"
max_concurrent_downloads = 5


if __name__ == "__main__":
    cookies_collection = create_cookies_from_browser_cookies(browser_cookies_file_path)
    save_cookies_to_file(cookies_collection, cookies_file_path)
    print(f"Cookies file created at: {cookies_file_path}")
    # download_videos(cookies_file_path, "./resources/links.txt")
    asyncio.run(
        download_videos_async(
            cookies_file_path, links_file_path, max_concurrent_downloads
        )
    )
