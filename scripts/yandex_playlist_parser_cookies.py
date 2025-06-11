#!/usr/bin/env python3
"""Parse a Yandex Music playlist using saved cookies."""

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

def scroll_to_bottom(page, step=1000):
    """Scroll page to the bottom to trigger lazy loading."""
    previous_height = 0
    while True:
        current_height = page.evaluate("document.body.scrollHeight")
        if current_height == previous_height:
            break
        page.evaluate(f"window.scrollBy(0, {step})")
        page.wait_for_timeout(500)
        previous_height = current_height


def main() -> None:
    """Launch browser, load playlist, and save track titles."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        cookies = parse_netscape_cookies(cookies_file)
        context.add_cookies(cookies)
        page = context.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_selector(
            '[aria-label^="Track "], [aria-label^="\u0422\u0440\u0435\u043a "]',
            timeout=30000,
        )

        # Ensure all tracks are loaded
        scroll_to_bottom(page)

        # Extract only track entries
        track_labels = page.eval_on_selector_all(
            '[aria-label^="Track "], [aria-label^="\u0422\u0440\u0435\u043a "]',
            "els => els.map(e => e.getAttribute('aria-label').replace(/^(Track|\\u0422\\u0440\\u0435\\u043a)\\s*/, ''))"
        )
        track_labels = list(dict.fromkeys(track_labels))

        os.makedirs('playlists', exist_ok=True)
        with open(f'playlists/{output_file}', 'w') as f:
            for track in track_labels:
                if track:
                    f.write(track.strip() + '\n')

        print(f'Saved {len(track_labels)} tracks to playlists/{output_file}')

        context.close()
        browser.close()


if __name__ == '__main__':
    main()
