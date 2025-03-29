import browser_cookie3
import time


def export_google_cookies(output_path="cookies.txt"):
    cj = browser_cookie3.load(domain_name=".google.com")
    drive_cj = browser_cookie3.load(domain_name="drive.google.com")

    with open(output_path, "w") as f:
        f.write("# Netscape HTTP Cookie File\n")
        for cookie in cj + drive_cj:
            expiry = cookie.expires or int(time.time()) + 31536000  # default 1 year
            f.write(
                f"{cookie.domain}\t{str(cookie.domain.startswith('.')).upper()}\t{cookie.path}\t{str(cookie.secure).upper()}\t{expiry}\t{cookie.name}\t{cookie.value}\n"
            )

    print(f"✅ Cookies saved to {output_path}")
    return output_path


# export_google_cookies("cookies.txt")
