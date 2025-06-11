from playwright.sync_api import sync_playwright
import os

url = "https://music.yandex.ru/users/nicholas28/playlists/1113"
output_file = "Live Chill Rave Meditation.txt"
cookies_file = "music.yandex.ru_cookies.txt"

def parse_netscape_cookies(filename):
    cookies = []
    with open(filename, "r") as f:
        for line in f:
            if line.strip().startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) == 7:
                domain, flag, path, secure, expiry, name, value = parts
                cookies.append({
                    "name": name,
                    "value": value,
                    "domain": domain,
                    "path": path,
                    "expires": int(expiry),
                    "httpOnly": False,
                    "secure": secure == "TRUE"
                })
    return cookies

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    cookies = parse_netscape_cookies(cookies_file)
    context.add_cookies(cookies)
    page = context.new_page()
    page.goto(url, timeout=60000)
    page.wait_for_selector('[aria-label]', timeout=30000)

    # Scroll until the page no longer loads new tracks
    last_height = 0
    last_count = 0
    while True:
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        page.wait_for_timeout(1000)
        current_height = page.evaluate('document.body.scrollHeight')
        current_count = len(page.query_selector_all('[aria-label]'))
        if current_height == last_height and current_count == last_count:
            break
        last_height = current_height
        last_count = current_count

    track_labels = page.eval_on_selector_all(
        '[aria-label]',
        "elements => elements.map(e => e.getAttribute('aria-label'))"
    )
    track_labels = list(dict.fromkeys(track_labels))

    os.makedirs("playlists", exist_ok=True)
    with open(f"playlists/{output_file}", "w") as f:
        for track in track_labels:
            f.write(track.strip() + "\n")

    print(f"Saved {len(track_labels)} tracks to playlists/{output_file}")

    browser.close()
