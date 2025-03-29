import datetime
import os


def get_unix_timestamp(expire_date):
    unix_timestamp = "1893456000"  # Default to a far future date
    if (
        expire_date != "" or expire_date != "0"
    ):  # Check if the date is not empty or zero
        exp = datetime.datetime.fromisoformat("2025-09-23T17:34:37.537+00:00")
        unix_timestamp = exp.timestamp()
    return str(int(unix_timestamp))


def get_domain_flag(domain):
    # Assuming http_only is a boolean string "true" or "false"
    return "TRUE" if domain.startswith(".") else "FALSE"


def get_secure_flag(secure):
    return "TRUE" if secure == "✓" else "FALSE"


def create_cookies_from_browser_cookies(browser_cookies_path):

    if not os.path.exists(browser_cookies_path):
        raise FileNotFoundError(f"Input file not found: {browser_cookies_path}")

    cookies = []
    cookies.append("# Netscape HTTP Cookie File")
    with open(browser_cookies_path, "r", encoding="utf-8") as raw_file:
        for line in raw_file:
            # Parse raw cookie data (assuming tab-separated values)
            parts = line.strip().split("\t")
            if len(parts) < 12:  # Ensure all fields are present
                continue  # Skip invalid lines

            # Extract fields based on the new structure
            (
                name,
                value,
                domain,
                path,
                expires_or_max_age,
                size,
                http_only,
                secure,
                same_site,
                partition_key,
                cross_site,
                priority,
            ) = parts

            # Replace invalid fields with valid values
            domain_flag = get_domain_flag(domain)
            secure_flag = get_secure_flag(secure)

            expires_or_max_age = get_unix_timestamp(expires_or_max_age)

            # Format the cookie data as needed
            cookies.append(
                f"{domain}\t{domain_flag}\t{path}\t{secure_flag}\t{expires_or_max_age}\t{name}\t{value}"
            )

    return cookies
    # with open(output_path, "w", encoding="utf-8") as cookies_file:
    #     cookies_file.write("\n".join(cookies))

    # return os.path.abspath(output_path)


def save_cookies_to_file(cookies, output_path):
    with open(output_path, "w", encoding="utf-8") as cookies_file:
        for cookie in cookies:
            cookies_file.write(cookie + "\n")
