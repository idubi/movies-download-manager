from src.cookies_authentication import (
    create_cookies_from_browser_cookies,
    save_cookies_to_file,
)
from src.movie_utils import download_videos
from src.gpt_browser_cookies import export_google_cookies

browser_cookies_file_path = "./resources/raw-cookies.txt"
cookies_file_path = "./resources/cookies.txt"
video_links_path = "./resources/links.txt"

if __name__ == "__main__":
    cookies_collection = create_cookies_from_browser_cookies(browser_cookies_file_path)
    save_cookies_to_file(cookies_collection, cookies_file_path)
    print(f"Cookies file created at: {cookies_file_path}")
    download_videos(cookies_file_path, "./resources/links.txt")
